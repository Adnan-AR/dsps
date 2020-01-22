defmodule DataError do
  @moduledoc"""
  Errors concerning patters (data), e.g. adding or removing
  """
  defexception [:message]
  
  @impl true
  def exception(msg) do
    %DataError{message: msg}
  end
end
