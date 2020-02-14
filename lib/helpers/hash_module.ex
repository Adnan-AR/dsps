defmodule Helpers.Hash do
  @moduledoc """
  Module that load the hash function used across the cluster
  """
  @doc """
  Hash function unsing md5 by default
  """
  def hash_string(string, algorithm \\ :md5),
    do: :crypto.hash(algorithm, string) |> Base.encode16

  @doc """
  Regroup patterns by length
  """
  def groupby_length(patterns) do
    Enum.reduce(patterns, %{}, fn(x, acc) ->
      Map.update(acc, String.length(x), [x], &(&1 ++ [x])) end)
  end

  @doc """
  Count string by length in Enumerable
  """
  def countby_length(patterns) do
    patterns
    |> Enum.reduce(%{}, fn x, acc ->
      Map.put(acc, String.length(x), Map.get(acc, String.length(x), 0) + 1)
    end) 
  end

  @doc """
  Chunk patterns by number of workers (list)
  e.g 
  Helpers.Hash.chunk_patterns([:a,:b,:c,:a,:b, :c, :k], 10)
    -> [[:a, :b, :c, :a, :b, :c, :k]]
  or Helpers.Hash.chunk_patterns([:a,:b,:c,:a,:b, :c, :k], 2)
    -> [[:a, :b, :c], [:a, :b, :c], [:k]] 
  """
  def chunk_patterns(patterns, workers_count) do
    patterns_count = length(patterns)
    if patterns_count < workers_count do
      patterns
      |> Enum.chunk_every(patterns_count)
    else
      patterns
      |> Enum.chunk_every(patterns_count |> div(workers_count))
    end
    
  end
  
  @doc """
  Chunk patterns by number of workers (map)
  e.g
  Helpers.Hash.chunk_patterns_byworkers(
         ["khar ","kleb","ayre","zob","hmar",
          "kesses","ayre&", "hal", "shagle", "ayre"], [:a, :b, :c])
    -> %{
          3 => [["zob", "hal"]], 
	  4 => [["kleb"], ["ayre"], ["hmar"], ["ayre"]],
	  5 => [["khar ", "ayre&"]],
	  6 => [["kesses", "shagle"]]
	}
  """
  def chunk_patterns_byworkers(patterns, workers) do
    # count all connected workers
    workers_count = workers |> length
    # We regroup patterns by length
    patterns_grouped = groupby_length(patterns)
    patterns_grouped
    |> Enum.reduce(%{}, fn {x, y}, acc ->
      Map.put(acc, x, chunk_patterns(y, workers_count)) end)
  end

  # count servers on each worker by length (used in global sharding)
  def workers_countby_length(length) do
    Helpers.ProcessesGetter.get_workers(:fetch_config)
    |> Enum.map(fn x ->
      {x, :rpc.call(x, MetaAgent, :get,[])
      |> Map.get(length, MapSet.new )} end)
    |> Enum.reduce(%{}, fn {x, y}, acc ->
      Map.put(acc, x, MapSet.size(y)) end)
  end
end
