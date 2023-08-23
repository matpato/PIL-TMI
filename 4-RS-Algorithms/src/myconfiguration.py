import configargparse


class MyConfiguration:
    __instance = None

    @staticmethod
    def get_instance() -> "MyConfiguration":
        """ Static access method. """
        if MyConfiguration.__instance is None:
            p = configargparse.ArgParser(default_config_files=['../configurations/configurations.ini'])

            p.add(
                '-mc',
                '--my-configurations',
                is_config_file=True,
                help='alternative configurations file path'
            )

            p.add(
                "-ds_folder",
                "--path_to_dataset_folder",
                required=False,
                help="path to dataset folder",
                type=str
            )

            p.add(
                "-cv",
                "--cv",
                required=False,
                help="cross validation folds",
                type=int
            )

            p.add("-k", "--topk", required=False, help="k for topk", type=int)
            p.add("-n", "--n", required=False, help="n most similar items", type=int)

            p.add(
                "-host",
                "--host",
                required=False,
                help="db host",
                type=str
            )
            p.add(
                '-port',
                '--port',
                required=False,
                help='db host port',
                type=str
            )
            p.add(
                "-user",
                "--user",
                required=False,
                help="db user",
                type=str
            )
            p.add(
                "-pwd",
                "--password",
                required=False,
                help="db password",
                type=str
            )
            p.add(
                "-db_name",
                "--database",
                required=False,
                help="db name",
                type=str
            )

            p.add(
                "-table_name",
                "--tablename",
                required=False,
                help="table name",
                type=str
            )

            p.add(
                "-owl",
                "--path_to_owl",
                required=False,
                help="path to owl ontology",
                type=str
            )
            p.add(
                "-db_onto",
                "--path_to_ontology_db",
                required=False,
                help="path to ontology db",
                type=str
            )
            p.add(
                "-metadata",
                "--path2info",
                required=False,
                help="path of metadata",
                type=str
            )
            p.add( "-path2res", "--path2res", required=False, help="path for results", type=str )

            p.add(
                "-sim_metric",
                "--similarity_metric",
                required=False,
                help="similarity metric acronym db",
                type=str
            )

            p.add(
                "-prefix",
                "--item_prefix",
                required=False,
                help="items prefix",
                type=str
            )
            p.add(
                "-n_split",
                "--n_split_dataset",
                required=False,
                help="number to split the list of entities",
                type=int
            )

            MyConfiguration(p.parse_args())

        return MyConfiguration.__instance

    def __init__(self, options):

        """
        Virtually private constructor.
        """
        if MyConfiguration.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.dataset_folder = options.path_to_dataset_folder

            self.cv = options.cv
            self.topk = options.topk
            self.n = options.n

            self.host = options.host
            self.port = options.port
            self.user = options.user
            self.password = options.password
            self.database = options.database
            self.tablename = options.tablename
            self.path_to_owl = options.path_to_owl
            self.path_to_ontology = options.path_to_ontology_db
            self.path2info = options.path2info
            self.path2res = options.path2res

            self.sim_metric = options.similarity_metric

            self.n_split = options.n_split_dataset
            self.item_prefix = options.item_prefix

        MyConfiguration.__instance = self


if __name__ == '__main__':
    s = MyConfiguration.get_instance()
    print(s)
    print(MyConfiguration.get_instance().host)
    print(MyConfiguration.get_instance().database)
    print(MyConfiguration.get_instance().user)
    print(MyConfiguration.get_instance().path_to_owl)
    print(MyConfiguration.get_instance().sim_metric)
    print(s.database)
