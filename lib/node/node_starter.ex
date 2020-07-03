defmodule Node.Starter do
  @moduledoc """
  Node Initializer
  """

  use Application
  @name __MODULE__
  # Rename node
  defp rename_node do
    # Fetch name
    lname = Application.fetch_env!(:dsps, :node_name)
    |> String.to_atom
    # rename the node
    :net_kernel.start([lname, :longnames])
  end

  # Set Cluster cookie (name)
  defp set_cookie do
    # Fetch the magic cookie (cluster name)
    Application.fetch_env!(:dsps, :cookie)
    |> String.to_atom
    |> Node.set_cookie
  end

  # Start node
  def start(_type, _args) do
    rename_node
    IO.inspect(Node.self)
    set_cookie
    node_t =  Application.fetch_env!(:dsps, :node_type)
    children = []
    # If it is a master
    children = if Map.get(node_t, "master") do
      # Add master to children
      Enum.concat(children, [{Master.Constructor, []}])
    else
      children
    end
    # If it is a worker
    children = if Map.get(node_t, "worker") do
      Enum.concat(children, [{Workers.Constructor, []}])
    else
      children
    end
    # If it is a client
    children = if Map.get(node_t, "client") do
      Enum.concat(children, [{Client.Constructor, []}])
    else
      children
    end
    IO.inspect(children)
    opts = [strategy: :one_for_one, name: @name]
    Supervisor.start_link(children, opts)
  end
end



    
  
