defmodule StringMatching.Dsupervisor do
  @moduledoc"""
  Dynamic supervisor of StringMatching processes
  """
  use DynamicSupervisor
  alias StringMatching.Server.Interface, as: Worker
  alias StringMatching.Metadata, as: Agent
  alias Node.Metadata, as: MetaAgent
  @name __MODULE__

  @doc """
  Start the supervisor
  """
  def start_link(_arg) do
    DynamicSupervisor.start_link(__MODULE__, :ok, name: @name)
  end

  @doc """
  Init the OTP supervisor
  """
  def init(:ok),
    do: DynamicSupervisor.init(strategy: :one_for_one)

  @doc """
  Start and supervise StringMatching server
  """
  def start_string_matching(child_name) do
    param = {Worker, :start_link, [child_name]}
    spec = %{id: Worker, start: param, restart: :transient}
    DynamicSupervisor.start_child(__MODULE__, spec)
    # Create an agent for this worker
    param = {Agent, :start_link, [child_name, {[], 0, :empty}]}
    spec = %{id: Agent, start: param, restart: :transient}
    DynamicSupervisor.start_child(__MODULE__, spec)
    # Update the metadata of this node
    MetaAgent.add_server(child_name)
  end
end
