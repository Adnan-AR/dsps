defmodule Cluster.Sharders.Dsupervisor do
  @moduledoc"""
  Dynamic supervisor of StringMatching processes
  """
  use DynamicSupervisor
  alias Cluster.Sharder, as: Sharder
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
  def start_cluster_sharder(child_name) do
    # Create a dynamic supervisor for the cluster sharders
    param = {Sharder, :start_link, [child_name]}
    spec = %{id: Sharder, start: param, restart: :transient}
    DynamicSupervisor.start_child(__MODULE__, spec)
  end
end
