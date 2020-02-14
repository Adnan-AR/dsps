defmodule Node.Servers do
  @moduledoc """
  Agent to store node servers names.
  """
  use Agent
  @name __MODULE__
  
  @doc """
  Start the Metadata base
  """
  def start_link(servers_names) do
    fn -> servers_names end
    |> Agent.start_link(name: @name)
  end

  @doc """
  Get the list of servers in all workers
  """
  def get,
    do: Agent.get(@name, fn servers -> servers end)

  @doc """
  add server with a specific length
  """
  # l stands for length
  # new_s stands for new server
  def add_server(new_s, l) do
    handle_update = fn
      servers ->
	Map.put(servers, l, MapSet.put(
	      Map.get(servers,l, MapSet.new), new_s))
    end
    Agent.update(@name, handle_update)
  end
end
