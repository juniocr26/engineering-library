.PHONY: docs
docs:
	bundle exec ruby $(if $(filter project,$(DOCS_WORKFLOW)),lib/documentation/project_command.rb,lib/documentation/command.rb) $(DOCS_ARGS)
