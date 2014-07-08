module GrData (grdata, grdata', GrData(..)) where
import Data.Array
import qualified Data.Map as Map
import qualified Data.Set as Set
import Groups
import Groups.Subgroups
import qualified Groups.Types.Subset as Sub
import Groups.Internals  -- factor and Ternary

data GrData = GrData {
 gd_order      :: Int,  -- Rename "gd_size"?
 gd_abelian    :: Bool,
 gd_nilpotence :: Maybe Int,
 gd_solvable   :: Bool,
 gd_simple     :: Bool,
 gd_rank       :: Int,
 gd_exponent   :: Int,
 gd_quantities :: Array Int (Maybe (Int, Int, Int, Int))
  -- ^Mapping from n to:
  --  * number of elements of order n
  --  * number of subgroups of order n
  --  * number of normal subgroups of order n
  --  * number of conjugacy classes of order n
} deriving (Eq, Ord, Read, Show)

grdata :: Group -> GrData
grdata g = GrData {
  gd_order      = n,
  gd_abelian    = abel,
  gd_nilpotence = abel ?: Just 1 :? (nilpot ?: nilpotence g :? Nothing),
  gd_solvable   = nilpot || and [subQtys ! i /= 0 | i <- divisors,
						    gcd i (div n i) == 1],
  gd_simple     = n /= 1 && not (or [q /= 0 | (m,q) <- assocs normQtys, m /= 1, m /= n]),
  gd_rank       = Set.findMin $ Set.map Sub.size $ subs Map.! self,
  gd_exponent   = foldl lcm 1 [k | (k,a) <- assocs ords, a /= 0],
  gd_quantities = listArray (1,n) [mod n i == 0 ?: Just (ords ! i, subQtys ! i, normQtys ! i, ccQtys ! i) :? Nothing | i <- [1..n]]
 } where n        = g_size g
	 self     = Sub.total g
	 divisors = filter ((== 0) . mod n) [2..n]
	 subs     = subgroupGens g
	 ords     = freqArray (1,n) $ map snd $ elems $ gr_dat g
	 subQtys  = freqArray (1,n) $ map Sub.size $ Map.keys subs
	 normQtys = freqArray (1,n) $ map Sub.size $ filter isNormal
						   $ Map.keys subs
	 ccQtys   = freqArray (1,n) $ map Sub.size $ conjugacies g
	 abel     = isAbelian g
	 nilpot   = abel || and [subQtys ! (p^a) == normQtys ! (p^a)
				 | (p,a) <- factor n]

grdata' :: (String, Group, [String]) -> String
grdata' (name, g, props) = showData (name, grdata g, props)

showData :: (String, GrData, [String]) -> String
showData (name, dat, props) | gd_order dat == 1 = unlines [
  name,
  unwords $ "1 abelian nilpotent solvable" : props,
  -- "1",
  "rank=0",
  "exp=1",
  "nilpotence=0"
 ]
showData (name, dat, props) = unlines [
  name,
  unwords $ [
   show $ gd_order dat,
   gd_abelian dat ?: "abelian" :? "nonabelian",
   gd_nilpotence dat /= Nothing ?: "nilpotent" :? "nonnilpotent",
   gd_solvable dat ?: "solvable" :? "nonsolvable",  -- insoluble?
   gd_simple dat ?: "simple" :? "nonsimple"
  ] ++ props,
  "elements  =" ++ unwords [show i ++ ':' : show a
			    | (i,Just (a,_,_,_)) <- assocs $ gd_quantities dat],
  "subgroups =" ++ unwords [show i ++ ':' : show b
			    | (i,Just (_,b,_,_)) <- assocs $ gd_quantities dat],
  "normsubgrs=" ++ unwords [show i ++ ':' : show c
			    | (i,Just (_,_,c,_)) <- assocs $ gd_quantities dat],
  "conjugacies=" ++ unwords [show i ++ ':' : show d
			    | (i,Just (_,_,_,d)) <- assocs $ gd_quantities dat],
  "rank=" ++ show (gd_rank dat),
  "exp="  ++ show (gd_exponent dat),
  "nilpotence=" ++ maybe "nil" show (gd_nilpotence dat)
 ]

freqArray :: Ix a => (a,a) -> [a] -> Array a Int
freqArray b = accumArray (+) 0 b . map (\x -> (x,1))
