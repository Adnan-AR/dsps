defmodule StringMatching.Metadata do
  @moduledoc """
  Agent to store String Matching server info
  such us patterns and their size.
  """
  use Agent
  
  @doc """
  Start the Metadata base
  """
  def start_link(name, {patterns, size, last_world, patterns_length}) do
    fn -> {patterns, size, last_world, patterns_length} end
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
  Set the state of a certain StringMatching worker (server)
  """
  def set(name, {patterns, size, last_world}) do
    handle_update = fn
      {_, _, _, length} -> {patterns, size, last_world, length}
    end
    Agent.update(via(name), handle_update)
  end
  def set(name, length) do
    handle_update = fn
      {x, y, z, _} -> {x, y, z, length}
    end
    Agent.update(via(name), handle_update)
  end
  # Private: Register StringMatching processes under the supervisor pid
  defp via(name), do: StringMatching.Metadata.Registry.via(name)
end
