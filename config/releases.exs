import Config

nodes = %{
    prod: %{
      :masters =>
      ["master@ip-10-0-10-138.eu-west-3.compute.internal"],
      :workers =>
	["worker1@ip-10-0-10-234.eu-west-3.compute.internal",
	 "worker2@ip-10-0-10-130.eu-west-3.compute.internal",
	 "worker3@ip-10-0-10-208.eu-west-3.compute.internal",
	 "worker4@ip-10-0-10-24.eu-west-3.compute.internal",
	 "worker5@ip-10-0-10-213.eu-west-3.compute.internal",
	 "worker6@ip-10-0-10-188.eu-west-3.compute.internal",
	 "worker7@ip-10-0-10-58.eu-west-3.compute.internal",
	 "worker8@ip-10-0-10-152.eu-west-3.compute.internal",
	 "worker9@ip-10-0-10-22.eu-west-3.compute.internal",
	 "worker10@ip-10-0-10-161.eu-west-3.compute.internal"],
      :clients =>
	["client@ip-10-0-10-85.eu-west-3.compute.internal"]
    },
    dev: %{
      :masters => ["node1@adnans-macbook-pro.home"],
      :workers =>
	["node2@adnans-macbook-pro.home","node3@adnans-macbook-pro.home",
	 "node4@adnans-macbook-pro.home","node6@adnans-macbook-pro.home"],
      :clients => ["node5@adnans-macbook-pro.home"]
    }
}

config :dsps,
  nodes1: Map.get(nodes, :prod)
