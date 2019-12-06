defmodule StringMatching.Metadata do
  @moduledoc """
  Agent to store String Matching server info
  such us patterns and their size.
  """
  use Agent
  
  @doc """
  Start the Metadata base
  """
  def start_link(name, {patterns, size, last_world}) do
    fn -> {patterns, size, last_world} end
    |> Agent.start_link(name: via(name))
  end

  @doc """
  Get the state of a certain StringMatching worker (server)
  """
  def get(name),
    do: Agent.get(via(name), fn{x,y,z} -> {x,y,z} end)
  def get(:size, name),
    do: Agent.get(via(name), fn{_,x,_} -> x end)
  def get(:last_word, name),
    do: Agent.get(via(name), fn{_,_,x} -> x end)
  def get(:patterns, name),
    do: Agent.get(via(name), fn{x,_,_} -> x end)

  @doc """
  Set the state of a certain StringMatching worker (server)
  """
  def set(name, {patterns, size, last_world}) do
    #IO.inspect(patterns)
    handle_update = fn
      {_, _, _} -> {patterns, size, last_world}
    end
    Agent.update(via(name), handle_update)
  end
  # Private: Register StringMatching processes under the supervisor pid
  defp via(name), do: StringMatching.Metadata.Registry.via(name)
end
