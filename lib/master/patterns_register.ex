defmodule Patterns.Register do
  @moduledoc """
  Agent to store patterns while reading from large set of data.
  """
  use Agent
  @name __MODULE__
  
  @doc """
  Start the Metadata base
  """
  def start_link(name, length) do
    fn -> {MapSet.new([]), length} end
    |> Agent.start_link(name: via(name))
  end

  @doc """
  Get the list of servers in all workers
  """
  def get(name),
    do: Agent.get(via(name), fn data -> data end)

   @doc """
  Add one pattern
  """
  def add_patterns(name, pattern) when is_binary(pattern) do
    # p stands for patterns
    # l stands for length
    string_length = String.length(pattern)
    handle_add = fn
      {p, l} when l == string_length ->
	patterns = MapSet.put(p, pattern)
        {patterns, l}
      {p, l} -> {p, l}
    end 
    Agent.update(via(name), handle_add)
  end
  @doc """
  Add list of patterns
  """
  # p_f stands for filtered patterns
  def add_patterns(name, patterns) do
    handle_add = fn
      {p, l} ->
	p_f = patterns
        |> Enum.filter(fn x -> String.length(x) == l end)
        |> MapSet.new
        |> MapSet.union(p)
        {p_f, l}
    end
    Agent.update(via(name), handle_add)
  end

  # Private: Register StringMatching processes under the supervisor pid
  defp via(name), do: Patterns.Register.Registry.via(name)
end
