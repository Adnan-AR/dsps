defmodule StringMatching.Server do
  @moduledoc """
  DspsSystem using GenServer.
  """
  @behaviour StringMatching.Interface.Behaviour
  @sm_api Application.fetch_env!(:dsps, :sm_algorithm)
  use GenServer
  require Logger
  
  @doc """
  API: start an StringMatching process
  """
  def start_link(name) do
    Logger.info("StringMatching automaton created: #{name}")
    GenServer.start_link(__MODULE__, :ok, name: via(name))
  end

  @doc """
  API: stop the automaton
  """
  def stop(name), do: GenServer.stop(via(name))
 
  @doc """
  API: crash
  """
  def crash(name), do: GenServer.cast(via(name), :raise)

  @doc """
  API: create automaton from patterns
  """
  def update(name, patterns),
    do: GenServer.cast(via(name), {:update, patterns})

  @doc """
  API: search for patterns in a given string
  """
  def search(name, string) do
    GenServer.call(via(name), {:search, name, string})
  end

  # Callbacks
  @doc """
  Callback: Init the OTP server
  """
  def init(name) do
    Logger.info("Starting #{inspect(name)}")
    {:ok, name}
  end

  @doc """
  Callback: terminate StringMatching worker
  """
  def terminate(reason, name) do
    Logger.info("terminate: #{name} with reason: #{inspect reason}")
  end
  
  @doc """
  Create StringMatching automaton
  """
  def handle_cast({:update, patterns}, _state) do
    # Replace the automaton
    state = @sm_api.new(patterns)
    # reply
    {:noreply, state}
  end

  @doc """
  Handle crash and raise
  """
  def handle_cast(:raise, name),
    do: raise RuntimeError, message: "Error, Server #{name} has crashed"

  @doc """
  Search for patterns in a string
  """
  def handle_call({:search, _name, string}, _from, state) do
    results = @sm_api.search(state, string)
    |> MapSet.to_list    
    {:reply, results, state}
  end

  # Private: Register StringMatching processes under the supervisor pid
  defp via(name), do: StringMatching.Servers.Registry.via(name)
  
end
