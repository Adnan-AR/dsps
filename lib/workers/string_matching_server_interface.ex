defmodule StringMatching.Server.Interface do
  @moduledoc """
  Aho-Corasick server interface.
  """
  
  @sm_server Application.fetch_env!(:dsps, :string_matching)
  defmodule Behaviour do
    @callback start_link(String.t, Integer.t) :: {:ok, Pid.t()}
                                                 | {:error, term}
    @callback stop(String.t) :: :ok | {:error, String.t()}
    @callback crash(String.t) :: :ok | {:erro, String.t()}
    #@callback add(String.t, String.t) :: :ok | {:error, String.t()}
    @callback update(String.t, list(String.t) | String.t) :: :ok
                                                | {:ok, String.t()}
    @callback search(String.t, String.t) :: MapSet.t()
                                                | {:error, String.t()}
  end

  @spec start_link(String.t, Integer.t) :: {:ok, Pid.t()} | {:error, term}
  def start_link(name, length), do: @sm_server.start_link(name, length)
  @spec stop(String.t) :: :ok | {:error, String.t()}
  def stop(name), do: @sm_server.stop(name)
  @spec crash(String.t) :: :ok | {:erro, String.t()}
  def crash(name), do: @sm_server.stop(name)
  @spec update(String.t, list(String.t) | String.t) :: :ok | {:ok, String.t()}
  def update(name, patterns), do: @sm_server.update(name, patterns)
  @spec search(String.t, String.t ) :: MapSet.t() | {:error, String.t()}
  def search(name, string), do: @sm_server.search(name, string)
  #@spec add(String.t, String.t ) :: :ok | {:error, String.t()}
  #def add(name, string), do: @sm_server.add(name, string)
end
