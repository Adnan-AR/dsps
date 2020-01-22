defmodule AlreadyExistError do
  @moduledoc"""
  Error if the added pattern already exists in the cluster
  """
  defexception [:message]
  
  @impl true
  def exception(value) do
    msg = "'#{value}' already exits in the cluster"
    %AlreadyExistError{message: msg}
  end
end
