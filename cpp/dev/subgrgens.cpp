#include <iostream>
#include <algorithm>
#include <deque>
#include <iterator>
#include <queue>
#include <set>
#include <utility>
#include "Groups/BasicGroup.hpp"
#include "Groups/Families/Symmetric.hpp"
using namespace std;
using namespace Groups;

template<class T> set<T> cycle(const basic_group<T>& g, const T& x) {
 const T id = g.identity();
 set<T> cyke;
 cyke.insert(id);
 T y = x;
 while (y != id) {
  cyke.insert(y);
  y = g.oper(y,x);
 }
 return cyke;
}

template<class T>
set<T> union(const set<T>& a, const set<T>& b) {
 set<T> c;
 std::set_union(a.begin(), a.end(), b.begin(), b.end(), std::inserter(c, c.end()));
 return c;
}

template<class T>
set<T> difference(const set<T>& a, const set<T>& b) {
 set<T> c;
 std::set_difference(a.begin(), a.end(), b.begin(), b.end(), std::inserter(c, c.end()));
 return c;
}

template<class T>
void update(set<T>& a, const set<T>& b) {
 // TODO: Which of these two is faster?
 //a = union(a,b);
 a.insert(b.begin(), b.end());
}

/**
  * Given two subsets of a group that are already closed under the group
  * operation (i.e., that are subgroups; this precondition is not checked),
  * subgroupUnion() computes the closure of their union.
  **/
template<class T>
set<T> subgroupUnion(const basic_group<T>& g, const set<T>& a, const set<T>& b)
{
 queue<T> nova(deque<T>(a.begin(), a.end()));
 set<T> seen = union(a,b);
 while (!nova.empty()) {
  T x = nova.front();
  nova.pop();
  const set<T> seenCopy(seen);
  for (const T& y: seenCopy) {
   T z1 = g.oper(x,y);
   if (seen.insert(z1).second) nova.push(z1);
   T z2 = g.oper(y,x);
   if (seen.insert(z2).second) nova.push(z2);
  }
 }
 return seen;
}

template<class T>
pair<set<T>, set<set<T> > >
addCycle(const basic_group<T>& g,
	 const set<T>& cyc,   const set< set<T> >& gs,
	 const set<T>& subgr, const set< set<T> >& gens) {
 /* TODO: Is there any reason for this to only check singletons?  What effect
  * would checking whether the first element of `gs` was a subset of `subgr`
  * have on performance? */
 typename set< set<T> >::const_iterator gsiter;
 for (gsiter = gs.begin(); gsiter != gs.end(); gsiter++) {
  const set<T>& cgSet = *gsiter;
  if (cgSet.size() == 1) {
   const T& cg = *cgSet.begin();
   if (subgr.count(cg) > 0) return make_pair(set<T>(), set<set<T> >());
   typename set<set<T> >::const_iterator gensIter;
   for (gensIter = gens.begin(); gensIter != gens.end(); gensIter++) {
    const set<T>& h = *gensIter;
    if (h.size() == 1) {
     if (cyc.count(*h.begin()) > 0) return make_pair(set<T>(), set<set<T> >());
     else break;
    }
   }
   set<T> newSubgr = subgroupUnion(g, subgr, cyc);
   set< set<T> > newGens;
   for (const set<T>& a: gens) {
    for (const set<T>& b: gs) {
     newGens.insert(union(difference(a, cyc), b));
    }
   }
   return std::make_pair(newSubgr, newGens);
  }
 }
 return make_pair(set<T>(), set<set<T> >());
}

//template<class T> using SetWGens = pair<set<T>, set<set<T>>>;

template<class T>
map< set<T>, set< set<T> > > subgroupGens(const basic_group<T>& g) {
 map< set<T>, set< set<T> > > cycles;
 const vector<T>& gelems = g.elements();
 typename vector<T>::const_iterator giter;
 for (giter = gelems.begin(); giter != gelems.end(); giter++) {
  set<T> single;
  single.insert(*giter);
  cycles[cycle(g, *giter)].insert(single);
 }
 map< set<T>, set< set<T> > > subgrs(cycles);
 typename map< set<T>, set< set<T> > >::iterator cyclesIter;
 for (cyclesIter = cycles.begin(); cyclesIter != cycles.end(); cyclesIter++) {
  const set<T>& cyc = cyclesIter->first;
  const set< set<T> >& gs = cyclesIter->second;
  if (cyc.size() == 1) continue;
  deque< pair<set<T>, set<set<T> > > > nova;
  typename map< set<T>, set< set<T> > >::iterator subgrsIter;
  for (subgrsIter = subgrs.begin(); subgrsIter != subgrs.end(); subgrsIter++) {
   pair<set<T>, set<set<T> > > newSub = addCycle(g, cyc, gs, subgrsIter->first,
						 subgrsIter->second);
   if (!newSub.first.empty()) nova.push_back(newSub);
  }
  typename deque< pair<set<T>, set<set<T> > > >::iterator novaIter;
  for (novaIter = nova.begin(); novaIter != nova.end(); novaIter++) {
   update(subgrs[novaIter->first], novaIter->second);
  }
 }
 return subgrs;
}

template<class T>
void showElemSet(const basic_group<T>& g, const set<T>& elems) {
 cout << '{';
 bool first = true;
 typename set<T>::const_iterator elemIter;
 for (elemIter = elems.begin(); elemIter != elems.end(); elemIter++) {
  if (first) first = false;
  else cout << ", ";
  cout << g.showElem(*elemIter);
 }
 cout << '}';
}

int main() {
 Symmetric g(4);
 typedef Symmetric::elem_t elem_t;
 map< set<elem_t>, set< set<elem_t> > > sg = subgroupGens(g);
 map< set<elem_t>, set< set<elem_t> > >::iterator sgiter;
 for (sgiter = sg.begin(); sgiter != sg.end(); sgiter++) {
  showElemSet(sgiter->first);
  cout << endl;
  set< set<elem_t> >::iterator gensiter;
  for (gensiter = sgiter->second->begin(); gensiter != sgiter->second->end(); gensiter++) {
   cout << ' ';
   showElemSet(*gensiter);
   cout << endl;
  }
  cout << endl;
 }
 return 0;
}
