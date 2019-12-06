defmodule Node.Metadata do
  @moduledoc """
  Agent to store node metada such us String Matching servers info.
  """
  use Agent
  @name __MODULE__
  
  @doc """
  Start the Metadata base
  """
  def start_link({how_many_servers, how_many_patterns, servers_names}) do
    fn -> {how_many_servers, how_many_patterns, servers_names} end
    |> Agent.start_link(name: @name)
  end

  @doc """
  Get the state of a specific Worker Node (server)
  """
  def get,
    do: Agent.get(@name, fn{x,y,z} -> {x,y,z} end)
  def get(:how_many_servers),
    do: Agent.get(@name, fn{x,_,_} -> x end)
  def get(:servers_names),
    do: Agent.get(@name, fn{_,_,x} -> x end)
  def get(:how_many_patterns),
    do: Agent.get(@name, fn{_,x,_} -> x end)

  @doc """
  Set the state of a specific StringMatching Node (server)
  """
  def set({how_many_servers, how_many_patterns, servers_names}) do
    handle_update = fn
      {_, _, _} -> {how_many_servers, how_many_patterns, servers_names}
    end
    Agent.update(@name, handle_update)
  end

  @doc """
  Increment the state of a specific node metadata (add servers)
  """
  def add_server(new_server) do
    handle_update = fn
      {x, y, servers} -> {x + 1, y, [new_server | servers]}
    end
    Agent.update(@name, handle_update)
  end

  @doc """
  Increment the state of a specific node metadata (add servers)
  """
  def add_patterns(words) do
    handle_update = fn
    {x, y, servers} when is_binary(words)
      -> {x, 1 + y, servers}
    {x, y, servers}
      -> {x, length(words) + y, servers}
    end
    Agent.update(@name, handle_update)
  end

end
