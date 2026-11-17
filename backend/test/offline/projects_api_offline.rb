require_relative "test_helper"
class ApiProjetosOfflineTest < CatalogoIsoladoTest
  def chamar(action, parameters)
    env = Rack::MockRequest.env_for("/api/projects/projeto", "action_dispatch.request.path_parameters" => { controller: "api/projects", action: action }.merge(parameters))
    status, headers, body = Api::ProjectsController.action(action).call(env)
    text = +""
    body.each { |part| text << part }
    body.close if body.respond_to?(:close)
    [status, headers, text]
  end
  def test_show_percorre_controlador_apresentador_e_arquivos_sem_banco
    project = projeto
    CatalogProject.stub(:find_by!, ->(**conditions) { assert_equal({ slug: "projeto", active: true }, conditions); project }) do
      status, _, body = chamar("show", { id: "projeto", lang: "en" })
      assert_equal 200, status
      assert_equal "Descrição sintética.", JSON.parse(body)["description"]
      assert_equal 1, JSON.parse(body)["categories"].size
    end
  end
  def test_arquivo_inacessivel_retorna_erro_neutro
    project = projeto
    File.delete(@root.join("projeto/en/bio.md"))
    CatalogProject.stub(:find_by!, project) do
      status, _, body = chamar("show", { id: "projeto", lang: "en" })
      assert_equal 503, status
      assert_equal({ "error" => "catalog_unavailable" }, JSON.parse(body))
      refute_includes body, @temporary
    end
  end
  def test_icone_valido_tem_csp_e_arquivo_invalido_nao_e_servido
    project = projeto
    CatalogProject.stub(:find_by!, project) do
      gravar("projeto/img/icon.webp", "RIFF0000WEBPsynthetic".b)
      status, headers, body = chamar("icon", { id: "projeto" })
      assert_equal 200, status
      assert_equal "image/webp", headers["content-type"].split(";").first
      assert_includes headers["content-security-policy"], "sandbox"
      assert_equal "RIFF0000WEBPsynthetic", body
      gravar("projeto/img/icon.webp", "SENTINELA")
      assert_equal 404, chamar("icon", { id: "projeto" }).first
    end
  end
end
