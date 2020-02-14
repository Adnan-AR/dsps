defmodule StringMatching.Metadata do
  @moduledoc """
  Agent to store String Matching server info
  such us patterns and their size.
  """
  use Agent
  
  @doc """
  Start the Metadata base
  """
  def start_link(name, {patterns, length}) do
    fn ->
      patterns =  patterns
      |> Enum.filter(fn x -> String.length(x) == length  end)
      |> MapSet.new
      {patterns, MapSet.size(patterns), Enum.at(patterns,-1), length} end
    |> Agent.start_link(name: via(name))
  end

  @doc """
  Get the state of a certain StringMatching worker (server)
  """
  def get(name),
    do: Agent.get(via(name), fn{x, y, z, w} -> {x, y, z, w} end)
  def get(:size, name),
    do: Agent.get(via(name), fn{_, x, _, _} -> x end)
  def get(:last_word, name),
    do: Agent.get(via(name), fn{_, _, x, _} -> x end)
  def get(:patterns, name),
    do: Agent.get(via(name), fn{x, _, _, _} -> x end)
  def get(:length, name),
    do: Agent.get(via(name), fn{_, _, _, x} -> x end)

  @doc """
  Add one pattern  
  """
  def add_patterns(name, pattern) when is_binary(pattern) do
    # p stands for patterns
    # s stands for size
    # l stands for length
    string_length = String.length(pattern)
    handle_add = fn
      {p, s, _last_world, l} when l == string_length ->
	patterns = MapSet.put(p, pattern)
        {patterns, MapSet.size(patterns), pattern, l}
      {p, s, last_world, l} -> {p, s, last_world, l}
    end 
    Agent.update(via(name), handle_add)
  end
  @doc """
  Add list of patterns
  """
  # p_f stands for filtered patterns
  def add_patterns(name, patterns) do
    handle_add = fn
      {p, s, last_world, l} ->
	p_f = patterns
        |> Enum.filter(fn x -> String.length(x) == l end)
        |> MapSet.new
        |> MapSet.union(p)
        {p_f, MapSet.size(p_f), Enum.at(p_f,-1), l}
    end
    Agent.update(via(name), handle_add)
  end

  @doc """
  Remove a list of patterns
  """
  def remove_patterns(name, patterns) do
    handle_add = fn
      {p, s, last_world, l} ->
	patterns = patterns |> MapSet.new
        new_p = MapSet.difference(p, patterns)
      {new_p, MapSet.size(new_p), Enum.at(new_p, -1), l}
    end
    Agent.update(via(name), handle_add)
  end
  
  # Private: Register StringMatching processes under the supervisor pid
  defp via(name), do: StringMatching.Metadata.Registry.via(name)
end
