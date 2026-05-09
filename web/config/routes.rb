Rails.application.routes.draw do
  root "dashboard#index"

  resources :articles, only: %i[index show] do
    member do
      post :translate
      post :post_to_platform
    end
  end

  get "search", to: "search#index"
  post "search/import", to: "search#import", as: :import_search
  post "search/pipeline", to: "search#pipeline", as: :pipeline_search

  resource :card_news, only: %i[new create] do
    post :generate_image
    get :download_image
    get :image, action: :serve_image
  end
  resource :settings, only: %i[show update]

  post "scrape", to: "articles#scrape"

  get "up" => "rails/health#show", as: :rails_health_check
end
