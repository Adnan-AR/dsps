defmodule Helpers.ProcessesGetter do
  @moduledoc"""
  Getter of running workers and supervisor in a supervisor tree
  """
  alias StringMatching.Server.Interface, as: Worker
  alias StringMatching.Metadata.Registry, as: AgentRegsitry
  alias StringMatching.Metadata, as: Agent
  alias Node.Servers, as: MetaAgent
  alias StringMatching.Servers.Registry, as: ServersRegistry
  
  @doc """
  Get workers under a supervisor
  """
  # Get workers from config file (only connected)
  def get_workers(:fetch_config) do
    connected_nodes = Node.list
    |> Enum.map(fn x -> Atom.to_string x end)
    |> MapSet.new
    Application.get_env(:dsps, :workers)
    |> MapSet.new
    |> MapSet.intersection(connected_nodes)
    |> MapSet.to_list
    |> Enum.map(fn x -> String.to_atom x end)
  end
  # Get workers, empty or not_empty
  def get_workers(supervisor_id) do
    # Get StringMatching servers names only whithout their agents
    handle_result = fn
      {_, x, :worker, [Worker]} -> [x]
      {_, _, :worker, [Agent]} -> []
    end
    DynamicSupervisor.which_children(supervisor_id)
    |> Enum.flat_map(handle_result)
    |> Enum.map(fn x -> Enum.at(Registry.keys(ServersRegistry, x),0) end)
  end
  # Get workers that contains at least one pattern
  def get_workers(supervisor_id, :not_empty) do
    get_workers(supervisor_id)
    |> Enum.filter(fn x -> Agent.get(:size, x) > 0 end)
  end
  
  @doc """
  Get agents a supervisor
  """
  # Get agents
  def get_agents(supervisor_id) do
    handle_result = fn
      {_, _, :worker, [Worker]} -> []
      {_, x, :worker, [Agent]} -> [x]
    end
    # Get the shard that contains the least number of patterns
    DynamicSupervisor.which_children(supervisor_id)
    |> Enum.flat_map(handle_result)
    |> Enum.map(fn x -> Enum.at(Registry.keys(AgentRegsitry, x),0) end)
  end
end
