#include <cstdio>
struct Sink { int writes = 0; };
struct Base {
  virtual ~Base() = default;
  virtual void clear() {}
  virtual bool empty() const { return false; }
  virtual void write(Sink&) const {}
  void write(Sink& sink, const char*) const { write(sink); }
};
int main() { Base base; Sink sink; base.clear(); base.write(sink); std::printf("{\"empty\":%d,\"writes\":%d}\n", base.empty(), sink.writes); }
