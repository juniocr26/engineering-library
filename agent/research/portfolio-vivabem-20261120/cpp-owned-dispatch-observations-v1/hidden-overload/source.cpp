#include <cstdio>
struct Sink { int writes = 0; };
struct Base {
  virtual ~Base() = default;
  virtual void clear() {}
  virtual bool empty() const { return false; }
  virtual void write(Sink&) const {}
  void write(Sink& sink, const char*) const { write(sink); }
};
struct Derived : Base {
  void write(Sink& sink) const override { ++sink.writes; }
  bool empty() const override { return true; }
};
int main() { Derived derived; Sink sink; derived.write(sink, "node"); }
