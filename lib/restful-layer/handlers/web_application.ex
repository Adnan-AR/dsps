defmodule WebApplication do
  @moduledoc"""
  Web application starter
  """
  def init, do: :ok

  @doc"""
  Run the Web Application (Empty)
  """
  def run do
    dispatch_config = :cowboy_router.compile([
      { :_,
	[
	  # {"/", PageHandler, args},
	  {"/search", SearchHandler, :ok},
	  {"/inject", UpdateHandler, :ok},
	  # {:_, Error404Handler, args}
	]
      }
    ])
    # Launch the cowboy application
    :cowboy.start_http(
      :http, 100,[{:port, 8080}],
      [{ :env, [{:dispatch, dispatch_config}]}]
    )
  end
  
end
