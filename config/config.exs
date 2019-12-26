import Config

# Setting String search algorithm
config :dsps,
  nodes: %{
    :masters =>
      ["master@ip-10-0-10-138.eu-west-3.compute.internal"],
    :workers =>
      ["worker1@ip-10-0-10-234.eu-west-3.compute.internal",
       "worker2@ip-10-0-10-130.eu-west-3.compute.internal",
       "worker3@ip-10-0-10-208.eu-west-3.compute.internal",
       "worker4@ip-10-0-10-24.eu-west-3.compute.internal",
       "worker5@ip-10-0-10-213.eu-west-3.compute.internal"],
    :clients =>
      ["client@ip-10-0-10-85.eu-west-3.compute.internal"]
  },
  nodes_: %{
    :masters =>
      ["node1@adnans-macbook-pro.home"],
    :workers =>
      ["node2@adnans-macbook-pro.home",
       "node3@adnans-macbook-pro.home",
       "node4@adnans-macbook-pro.home",
       "node6@adnans-macbook-pro.home"],
    :clients =>
      ["node5@adnans-macbook-pro.home"]
  }


# Setting loaded module depending on the env, Mock if test
case Mix.env do
  :test -> config :dsps, string_matching: RabinKarp.Server
  _ -> config :dsps, string_matching: RabinKarp.Server
end
