struct Base {
    virtual ~Base() = default;
    virtual int value() const { return 1; }
};
struct Derived : Base {};
struct Further : Derived {
    int value() const override { return 2; }
};
int unqualified(Derived& object) { return object.value(); }
int qualified(Derived& object) { return object.Base::value(); }
