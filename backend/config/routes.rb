Rails.application.routes.draw do
  namespace :api do
    resource :note_demos, only: [:create, :destroy] if Rails.env.development?
    resources :notes, only: [:index, :create, :update, :destroy]
    resources :highlights, only: [:index, :create, :update, :destroy]
    resources :bookmarks, only: [:index, :create, :destroy]
    resources :projects, only: [:index, :show] do
      get :icon, on: :member
    end
  end
  # Define your application routes per the DSL in https://guides.rubyonrails.org/routing.html

  # Reveal health status on /up that returns 200 if the app boots with no exceptions, otherwise 500.
  # Can be used by load balancers and uptime monitors to verify that the app is live.
  get "up" => "rails/health#show", as: :rails_health_check

  # Defines the root path route ("/")
  # root "posts#index"
end
