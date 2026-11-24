function target() { return 1; }
function outer() {
  target();
  target.call(this);
  target.apply(this, []);
  const alias = target;
  alias();
  const obj = {target};
  obj.target();
  obj['target']();
  [1].map(() => target());
}
function shadow(target) { target(); target.call(this); }
