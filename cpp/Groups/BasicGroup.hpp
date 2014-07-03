#ifndef BASICGROUP_H
#define BASICGROUP_H

#include <string>
#include <vector>
#include "closure.hpp"

namespace Groups {
 template<class T> class basic_group {
 public:
  typedef T elem_t;
  virtual ~basic_group() { }
  virtual T oper(const T&, const T&) const = 0;
  virtual T identity() const = 0;
  virtual T invert(const T&) const = 0;
  virtual int order() const = 0;
  virtual int order(const T&) const = 0;
  virtual std::vector<T> elements() const = 0;
  virtual std::string showElem(const T&) const = 0;
  virtual bool abelian() const = 0;
  virtual basic_group<T>* copy() const = 0;
  virtual int cmp(const basic_group<T>*) const = 0;
  virtual bool contains(const T&) const = 0;

  std::set<T> closure(const std::set<T>& start) const {
   return closure2A<T>(opcall(this), start.begin(), start.end());
  }

  template<class Iter>
  std::set<T> closure(Iter first, Iter last) const {
   return closure2A<T>(opcall(this), first, last);
  }

 private:
  struct opcall {  // TODO: Look for a better way to accomplish this.
   const basic_group<T>* g;
   opcall(const basic_group<T>* h) : g(h) { }
   T operator()(const T& x, const T& y) const {return g->oper(x,y); }
  };
 };
}

#endif
