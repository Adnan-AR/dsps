defmodule Helpers.Benchmarkers do
  @moduledoc """
  Contains benchmark tools for the DSPS
  """

  @doc """
  Measure the runtime of a function
  """  
  def measure_runtime(function) do
    function
    |> :timer.tc
    |> elem(0)
    |> Kernel./(1_000_000)
  end
  
end
