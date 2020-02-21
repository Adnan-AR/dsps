import Config

# Setting loaded module depending on the env, Mock if test
case Mix.env do
  :test ->
    config :dsps,
      string_matching: RabinKarp.Server
  :dev ->
    config :dsps,
      string_matching: RabinKarp.Server
  :prod ->
    config :dsps,
      string_matching: RabinKarp.Server
end
