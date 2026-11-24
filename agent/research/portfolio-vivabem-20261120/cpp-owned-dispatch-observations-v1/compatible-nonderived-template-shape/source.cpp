#include <cstdio>
struct NotDerived {
  int reads = 0;
  static NotDerived* create() { static NotDerived object; return &object; }
  void read(int) { ++reads; }
  bool empty() const { return reads == 0; }
};
template<class T> T* createAndRead(int value) {
  T* object = T::create();
  object->read(value);
  return !object->empty() ? object : nullptr;
}
int main() { NotDerived* object = createAndRead<NotDerived>(1); std::printf("{\"accepted\":%d,\"reads\":%d}\n", object != nullptr, object ? object->reads : -1); }
