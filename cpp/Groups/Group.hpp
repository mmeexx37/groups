#ifndef GROUP_H
#define GROUP_H
#include <string>
#include <vector>
#include "closure.hpp"
namespace Groups {
 template<class T> class group {
 public:
  typedef T elem_t;
  virtual ~group() { }
  virtual T op(const T&, const T&) const = 0;
  virtual T identity() const = 0;
  virtual T invert(const T&) const = 0;
  virtual int order() const = 0;
  virtual int order(const T&) const = 0;
  virtual std::vector<T> elements() const = 0;
  virtual std::string showElem(const T&) const = 0;
  virtual bool abelian() const = 0;
  virtual group<T>* copy() const = 0;
  virtual int cmp(const group<T>*) const = 0;
  virtual bool contains(const T&) const = 0;

 private:
  struct opcall {  // TODO: Look for a better way to accomplish this.
   const group<T>* g;
   opcall(const group<T>* h) : g(h) { }
   T operator()(const T& x, const T& y) const {return g->op(x,y); }
  };

 public:
  std::set<T> closure(const std::set<T>& start) const {
   return closure2A<T>(opcall(this), start.begin(), start.end());
  }

  template<class Iter>
  std::set<T> closure(Iter first, Iter last) const {
   return closure2A<T>(opcall(this), first, last);
  }
 };
}
#endif
