defmodule Helpers.FileExt do
  @moduledoc """
  Files handler module
  """

  @doc """
  List all files in a directory
  """
  def ls_r(path \\ ".") do
    cond do
      File.regular?(path) -> [path]
      File.dir?(path) ->
        File.ls!(path)
        |> Enum.map(&Path.join(path, &1))
        |> Enum.map(&ls_r/1)
        |> Enum.concat
      true -> []
    end
  end

  @doc """
  Read csv files and get the first column as a list
  TODE: to be removed
  """
  def read_dictionary(path, take \\ :all) when take == :all do
    path
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.map(fn x -> Enum.at(x,0) end)
  end
  def read_dictionary(path, take) when is_integer(take) do
    path
    |> Path.expand(__DIR__)
    |> File.stream!
    |> CSV.decode!
    |> Enum.take(take)
    |> Enum.map(fn x -> Enum.at(x,0) end)
  end
end
