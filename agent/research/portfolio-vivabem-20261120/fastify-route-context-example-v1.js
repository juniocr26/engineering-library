function defineRoutes(app) {
  app.register(function prefixed(scope, _options, done) {
    scope.route({
      method: ['HEAD'],
      url: '/',
      handler(_request, reply) { reply.send(); }
    });
    done();
  }, { prefix: '/api' });
}
