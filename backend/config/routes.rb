Rails.application.routes.draw do
  namespace :api do
    resources :annotations, only: [:index]
    if Rails.env.development?
      get 'note_demos', to: 'note_demos#index'
      resource :note_demos, only: [:create, :destroy]
    end
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
