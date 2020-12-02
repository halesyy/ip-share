import json
import time
import datetime
from yahooquery import Ticker

class Packer:

    disher = {
        "xls":  "excel",
        "xlsx": "excel",
        "csv":  "csv",
        "txt":  "txt",
        "yfi":  "yfi"
    }

    def __init__(self):
        self.datasets = []
        self.cache = self.getCache()
        self.empty = ["nan", "NaN", "false", "False"]
        self.ids = []
        self.names = ["string:Date"]
        self.meta = [] # meta-datasets, saves

    def addEmpty(self, em):
        self.empty += em

    def getCache(self):
        with open("cache.json", "r+") as f:
            data = str(f.read())
        return json.loads(data)

    def updateCache(self):
        data = self.cache
        with open("cache.json", "w+") as f:
            f.write(json.dumps(data, indent=3))

    """
    Takes a EXCEL URL and parses it out.
    """
    def excel(self, url, options):
        import shutil
        import requests as req
        import pandas as pd
        headers = {} if "headers" not in options else options["headers"]
        r = req.get(url, stream=True, headers=headers)
        # open("tmp/r.html", "w+").write(r.text)
        with open("tmp/ex.xlsx", "wb+") as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

        if "sheet" in options and "skip" in options:
            sheet = pd.read_excel("tmp/ex.xlsx", options["sheet"], skiprows=options["skip"])
        else:
            sheet = pd.read_excel("tmp/ex.xlsx")

        return sheet

    """
    yfinance puller, simplifier.
    """
    def yfi(self, identifier, options):
        # convert
        convert = {"daily": "1d", "monthly": "1m", "weekly": "1w"}
        ticker = identifier.split(".yfi")[0]
        stockObject = Ticker(ticker)
        history = stockObject.history(period="max", interval=convert[options["range"]])
        return history

    """
    csv manager
    """
    def csv(self, url, options):
        import shutil
        import requests as req
        import pandas as pd
        r = req.get(url, stream=True)
        with open("tmp/csv.csv", "wb+") as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
        sheet = pd.read_csv("tmp/csv.csv")
        if "reverse" in options and options["reverse"] == True:
            sheet = sheet.reindex(index=sheet.index[::-1])
        return sheet


    """
    Shorthand dataset functions.
    """
    def d_csv(self, id, url, index, subset, name=False):
        options = {
            "url": url,
            "parse_as": "csv",
            "index": index,
            "subsets": [subset],
            "scrape_every": "1 day"
        }
        self.dataset(id, options)
        self.ids.append(id)
        if name != False: self.names.append(name)

    """
    | fred collaborator, pulls from fred
    """
    def d_fred(self, id, csvlink, subset):
        # dataset = csvlink.split("/")[-1]
        self.d_csv(id, csvlink, "DATE", subset)

    """
    | yfinance collaboration
    """
    def d_yfi(self, id, url, name=False):
        options = {
            "url": url,
            "parse_as": "yfi",
            "index": "date",
            "range": "daily",
            "subsets": ["close"],
            "scrape_every": "1 day"
        }
        self.dataset(id, options)
        self.ids.append(id)
        if name != False: self.names.append(name)

    """
    Spawn a dataset into existence
    to be managed in the future.
    """
    def dataset(self, id, options):

        url = options["url"]
        filename = url.split(".")[-1]

        #= pauser for login requirement
        if "requires_login" in options and options["requires_login"] == True:
            print("{} requires a login".format(url))
            print("Press enter once you have confirmed you have logged into this website and:")
            print("1. stored user agent")
            print("2. stored cookie")
            input("3. other sensitive request information")


        #= check whether to scarpe dependent on cache

        if url in self.cache["url_check_cache"]:
            if self.cache["url_check_cache"][url] > time.time(): return print("[debug] no requirement to scrape [opt:url_check_cache]")
            else: pass
        else:
            self.cache["url_check_cache"][url] = 0

        #= parse type

        if filename in self.disher and "parse_as" not in options:
            method = getattr(self, self.disher[filename])
            frame = method(url, options)
        else:
            method = getattr(self, self.disher[options["parse_as"]])
            frame = method(url, options)

        #= cache update

        seconds = 1 if options["scrape_every"] == "1 day" else 0
        self.cache["url_check_cache"][url] = int(time.time()) + seconds
        self.updateCache()

        SUBSETS = {}

        dataset_index = options["index"]

        headers = frame.columns.values.tolist()
        indexes = list(frame.index.names)
        index_col = frame.index.values.tolist()

        # we have to unpack, find the index id, and run through at x
        # this is simply creating the index row, the x-axis
        if dataset_index in indexes:
            row_idx = indexes.index(dataset_index)
            INDEX_SUBSET = [row[row_idx] for row in index_col]
        elif dataset_index in headers:
            INDEX_SUBSET = list(frame[[ dataset_index ]].to_numpy())
            INDEX_SUBSET = [d[0] for d in INDEX_SUBSET]

        #= subset calculation
        for subset_name in options["subsets"]:
            subset = list(frame[[subset_name]].to_numpy())
            subset = [s[0] for s in subset]
            SUBSETS[subset_name] = subset

        # date_subset = list(frame[[options["date"]]].to_numpy())
        # date_subset = [d[0] for d in date_subset]

        self.datasets.append({
            "frame":                frame,
            "id":                   id,
            "original_options":     options,
            "subsets":              SUBSETS,
            "subsets_index":        INDEX_SUBSET
        })

        if "name" in options: self.names.append(options["name"])

    """
    Iterate through all subsets,
    and ensure their index has a date
    that can be assosiated.
    ---
    DOES NOT pair datasets by an anchor.
    Don't be mean.
    """
    def minimize(self, ids, normalize=False):

        local_datasets = []
        for ds_index, ds in enumerate(self.datasets):
            if ds["id"] in ids:
                local_datasets.append([ds_index, ds])

        # do filter on each dataset's subsets
        for ds_index, dataset in local_datasets:

            index_subset = dataset["subsets_index"]

            # creatng subsets
            subsets = {k: v for k, v in dataset["subsets"].items()}

            # get the length of the subsets for this DATASET
            subset_lens = [len(index_subset)]
            subset_lens += [len(subsets[sub]) for sub in subsets.keys()]

            # max iter due to limiting by minimum
            iter_to = min(subset_lens)

            # iter on the subsets, making minimum length
            # if one subset is 10 long, the user will have to
            # artificially extend it themselves. this is a
            # no-mercy algorithm. they can just extend on rest.
            # ----
            # res: NEW_SUBSETS
            NEW_SUBSETS = {}
            for colname, subset in subsets.items():
                _subset_data = []

                for i in range(iter_to):
                    index, item = index_subset[i], subset[i]
                    _subset_data.append(str(item))

                NEW_SUBSETS[colname] = _subset_data

            # iterate through each subset and normalize data.
            # if empty,empty,empty,5 - make all empty's 5
            # if 5,6,6,empty,empty,7 - make all empty's 6
            if normalize == True:

                _new_subsets = {}

                for subset_name, subset in NEW_SUBSETS.items():
                    # preset run state
                    # print("running over", subset_name, "with eg", str(subset[0:5]))
                    hit_data, last_data, fill_later = False, False, False
                    _subset = []
                    for data in subset:
                        # need to make a decision, contains an emty flag such as "nan"
                        if str(data) in self.empty:
                            print("this data is empty, fill_later triggered")
                            # print(data, "is apparnetly in empty reference")
                            _subset.append(last_data if hit_data else "FILL_LATER")
                            if hit_data == False: fill_later = True #no data found still
                        else:
                            hit_data, last_data = True, data
                            _subset.append(data)
                            if fill_later == True:
                                _subset = [s.replace("FILL_LATER", data) for s in _subset]
                            fill_later = False
                    _new_subsets[subset_name] = _subset

                NEW_SUBSETS = _new_subsets

            # printing out results
            # for k, v in NEW_SUBSETS.items():
                # print(k, v[0:4])
                # print(k, ["{:.2}".format(x) for x in v[0:5]])

            self.datasets[ds_index]["subsets"] = NEW_SUBSETS

        pass # end of func call to manage datasets

    def get_dataset_from_id(self, id):
        for ds_index, ds in enumerate(self.datasets):
            if ds["id"] == id:
                return [ds_index, ds]
        return False

    """
    Run through index of each dataset ID
    and parse as dates.
    """
    def parse_indexes_as_date(self, arr):
        import time, datetime, math
        from datetime import date

        for id, parse_func in arr:
            dataset = self.get_dataset_from_id(id)
            if dataset == False:
                print("Dataset with id {} could not be found".format(id))
                return False
            else:
                ds_index, dataset = dataset

            # dataset
            new_index = []
            # index_index = {} # LOL NO
            fdata_to_index, index_to_fdata, fdata_to_dayindex, dayindex_to_fdata = {}, {}, {}, {}
            for i, data in enumerate(dataset["subsets_index"]):
                function_return = parse_func(data)

                # calculate days since
                ymd = function_return.split("/")
                ymd = list(map(int, ymd))
                start = date(ymd[0], ymd[1], ymd[2])
                now = date.today()
                days_since_index = now - start

                new_index.append(function_return)

                fdata_to_dayindex[function_return] = "_{}".format(days_since_index.days)
                dayindex_to_fdata["_{}".format(days_since_index.days)] = function_return

                fdata_to_index[function_return] = "_{}".format(i)
                index_to_fdata["_{}".format(i)] = function_return

            self.datasets[ds_index]["subsets_index"] = new_index
            self.datasets[ds_index]["subsets_index_backrefs"] = {
                "fdata_to_index": fdata_to_index,
                "index_to_fdata": index_to_fdata,
                "fdata_to_dayindex": fdata_to_dayindex,
                "dayindex_to_fdata": dayindex_to_fdata
            }

    """
    iterate ober subset of dataset, and create
    a new one under the name subset_saveas as a simple
    moving average.
    """
    def sma(self, id, subset, period=25, saveas=False):
        dataset = self.get_dataset_from_id(id)
        if dataset != False:
            ds_index, ds = dataset

        sub = ds["subsets"][subset]
        sma_track = []

        for x, sub_data in enumerate(sub):
            sub_data = float(sub_data)
            # ignore till enough
            if x <= period:
                sma_track.append(sub_data)
                continue
            # get data
            sma_calc = []
            for b in range(x, x-period, -1): #sma lookback
                sma_calc.append(sub[b])
            sma_calc = sum(sma_calc)/len(sma_calc)
            sma_track.append(sma_calc)

        if saveas == False:
            self.datasets[ds_index]["subsets"][subset] = sma_track
        else:
            self.datasets[ds_index]["subsets"][saveas] = sma_track

    """
    inverse the subset
    """
    def inverse(self, id, subset):
        dataset = self.get_dataset_from_id(id)
        if dataset != False:
            ds_index, ds = dataset

        sub = ds["subsets"][subset].copy()
        inversed_subset = []

        for x, sub_data in enumerate(sub):
            # sub_data = float(sub_data) * -1
            inversed_subset.append( float(sub_data) * -1 )

        # print(sub[5])
        # print(inversed_subset[5])
        self.datasets[ds_index]["subsets"][subset] = inversed_subset

    def add(self, id, subset, adding):
        dataset = self.get_dataset_from_id(id)
        if dataset != False:
            ds_index, ds = dataset

        sub = ds["subsets"][subset].copy()
        multiplied_subset = []

        for x, sub_data in enumerate(sub):
            # sub_data = float(sub_data) * -1
            multiplied_subset.append( float(sub_data) + adding )

        # print(sub[5])
        # print(inversed_subset[5])
        self.datasets[ds_index]["subsets"][subset] = multiplied_subset

    def multiply(self, id, subset, multiplying):
        dataset = self.get_dataset_from_id(id)
        if dataset != False:
            ds_index, ds = dataset

        sub = ds["subsets"][subset].copy()
        multiplied_subset = []

        for x, sub_data in enumerate(sub):
            # sub_data = float(sub_data) * -1
            multiplied_subset.append( float(sub_data) * multiplying )

        # print(sub[5])
        # print(inversed_subset[5])
        self.datasets[ds_index]["subsets"][subset] = multiplied_subset


    """
    stack a subset
    """
    def stacked(self, id, subset, inverse=False):
        dataset = self.get_dataset_from_id(id)
        if dataset != False:
            ds_index, ds = dataset

        sub = ds["subsets"][subset]
        stacked = []

        for x, sub_data in enumerate(sub):
            if len(stacked) == 0:
                stacked.append(float(sub_data))
            else:
                stacked.append(stacked[-1] + float(sub_data))

        stacked = [s*-1 for s in stacked]
        self.datasets[ds_index]["subsets"][subset] = stacked

    def remove_dots(self, id, subset, empties=["."]):
        dataset = self.get_dataset_from_id(id)
        if dataset != False:
            ds_index, ds = dataset

        sub = ds["subsets"][subset]
        dotless = []
        last = 0

        for x, sub_data in enumerate(sub):
            if sub_data == ".":
                dotless.append(last)
            else:
                last = float(sub_data)
                dotless.append(last)
            # dotless.append( 0 )
            # dotless.append( 1 - (float(sub_data) / float(sub[x-1])) )

        # print(dotless)
        self.datasets[ds_index]["subsets"][subset] = dotless


    def percentages(self, id, subset):
        dataset = self.get_dataset_from_id(id)
        if dataset != False:
            ds_index, ds = dataset

        sub = ds["subsets"][subset]
        percentages = []

        for x, sub_data in enumerate(sub):
            if len(percentages) == 0:
                percentages.append( 0 )
            else:
                percentages.append( 1 - (float(sub_data) / float(sub[x-1])) )

        self.datasets[ds_index]["subsets"][subset] = percentages

    """
    # 1. store index [0] of list as x
    # 2. prepend x to list
    # 3. pop last value off list
    """
    def topple(self, id, subset):
        dataset = self.get_dataset_from_id(id)
        if dataset != False:
            ds_index, ds = dataset

        sub = ds["subsets"][subset]

        # sma_track = []
        topple_sub = sub
        topple_val = sub[0]
        topple_sub.insert(0, topple_val)
        topple_sub.pop()

        self.datasets[ds_index]["subsets"][subset] = topple_sub

    """
    create a new subset for a dataset
    """
    def meta_derive(self, meta_id, derive_name, callable):
        container = self.meta[meta_id]["container"]

        headers = self.meta[meta_id]["headers"]
        headers.append(derive_name)

        horizontal_requirement = len(headers)
        print("management headers: ", headers)

        derived_container = []

        for row in container:
            _row = self.possible_floats(row.copy())
            append_value = callable(_row)
            if append_value == False:
                print("Callable in meta_derive was false, wont allow")
                exit()
            _row.append(append_value)
            derived_container.append(_row)

        self.meta.append({
            "headers": headers,
            "container": derived_container
        })

        self.names.append("number"+str(meta_id))

        return len(self.meta)-1

    def possible_floats(self, li):
        newl = []
        for l in li:
            try:
                newl.append(float(l))
            except:
                newl.append(l)
        return newl

    """
    makes all values floats
    """
    def floats(self, meta_id):
        container = self.meta[meta_id]["container"]
        headers = self.meta[meta_id]["headers"]

        _container = []
        for row in container:
            _row = [row[0]]
            for data in row[1:]:
                _row.append(float(data))
            _container.append(_row)

        self.meta.append({
            "headers": headers,
            "container": _container
        })

        return len(self.meta)-1




    """
    brings all values from initialization to
    the same start
    """
    def same_start(self, meta_id):
        container = self.meta[meta_id]["container"]
        headers = self.meta[meta_id]["headers"]

        first_row_values = container[0]
        top_most = max(first_row_values[1:])

        normalizes = [-1] # ignore init [0]
        for to_change in first_row_values[1:]:
            # print(top_most, to_change)
            normalizes.append(top_most - to_change)
        print(normalizes)

        _container = []
        for row in container:
            _row = []
            _row.append(row[0])
            iter = 1
            for data in row[1:]:
                _row.append(data + normalizes[iter])
                iter += 1
            # print(_row)
            _container.append(_row)

        self.meta.append({
            "container": _container,
            "headers": headers
        })

        return len(self.meta)-1

    # result:
    # i want to be able to iterate through
    # a row that has the dates merged, where
    # it all links up together.
    # like
    # 1: [10-5-2021, 5.01025]
    # 2: [10-5-2021, 6.20152]
    # iterate as:
    # 3: [10-5-2021, 5.01, 6.20]
    # meta-datasets are going to be uber simple,
    # with a header row and a rows row
    def index(self, side_ids, by):
        local_datasets = []

        for id in side_ids:
            dataset = self.get_dataset_from_id(id)
            if dataset != False: local_datasets.append(dataset)
        pass

        # can iterate by datasets using, for id, dataset in local_datasets,
        # and get the subsets using dataset["subsets"]

        container = [] # the row-by-row struct
        headers   = [] # the headers for runparse

        # links a index back to it's original row
        container_linker = {}

        # anchor management, the barebones
        anchor_id, anchor_ds = self.get_dataset_from_id(by)
        # container_access = 0

        # fill up container with indexes
        headers.append("index")
        for refx, anchor_index in enumerate(anchor_ds["subsets_index"]):
            container.append([anchor_index])
            container_linker[anchor_index] = refx
        # container_access = 1

        containerx = len(container)

        for anchor_subset_name, anchor_subset in anchor_ds["subsets"].items():
            headers.append(anchor_subset_name)
            for i, anchor_data in enumerate(anchor_subset):
                container[i].append(anchor_data)

        indexes_included = container_linker.keys()
        # is a list of _x for all anchors
        anchor_backs = ["{}".format(anchor_ds["subsets_index_backrefs"]["fdata_to_dayindex"][index]) for index in indexes_included if index in anchor_ds["subsets_index_backrefs"]["fdata_to_dayindex"]]

        # jfc
        for ref_id, ref_dataset in local_datasets:
            ref_subsets = ref_dataset["subsets"]
            # on each subset's name and dataset it contains importantly
            for ref_subset_name, ref_subset_data in ref_subsets.items():
                headers.append(ref_subset_name)
                # iterateing by INDEX as well as SUBSETS DATA
                max_container_length = len(headers)
                data_iter = 0
                for ref_index, ref_data in zip(ref_dataset["subsets_index"], ref_subset_data):
                    if ref_index in indexes_included:
                        ciq = container[container_linker[ref_index]]
                        if len(ciq) < max_container_length:
                            container[container_linker[ref_index]].append(ref_data)
                        else:
                            container[container_linker[ref_index]][max_container_length-1] = ref_data
                    elif data_iter < 4:
                        continue
                    else:
                        fdata_to_index, index_to_fdata, fdata_to_dayindex, dayindex_to_fdata = ref_dataset["subsets_index_backrefs"].values()

                        day_index = int(fdata_to_dayindex[ref_index].replace("_", ""))
                        backs = ["_{}".format(x) for x in range(day_index-1, day_index-10, -1)]
                        # print("using backs: ", backs)
                        closest, closest_back, closest_container_id = False, False, False
                        for back in backs:
                            if back in anchor_backs:
                                # we have a hit ! place it in
                                closest_back = back
                                closest = ref_data
                                closest_container_id = anchor_ds["subsets_index_backrefs"]["dayindex_to_fdata"][back]

                        # turn closest
                        if closest != False and closest_back != False:
                            ciq = container[container_linker[closest_container_id]]
                            if len(ciq) < max_container_length:
                                container[container_linker[closest_container_id]].append(ref_data)
                            else:
                                container[container_linker[closest_container_id]][max_container_length-1] = ref_data

                    data_iter += 1

        self.meta.append({
            "container": container,
            "headers": headers
        })
        # print(headers)

        return len(self.meta)-1

    def split_array_vertically(self, container):
        subs = [[] for _ in range(len(container[0]))]

        for row in container:
            for i, data in enumerate(row):
                subs[i].append(data)

        return subs

    def vertical_combine(self, verticals):
        container = []
        horizontal = len(verticals)

        index_vertical = verticals[0]
        for data in index_vertical:
            container.append([data])

        # y-range
        for x in range(1, horizontal):
            for y, index in enumerate(container):
                container[y].append(verticals[x][y])

        return container

    """
    yay...
    """
    def clean(self, meta_id):
        container = self.meta[meta_id]["container"]
        # print(container)
        # print(container)
        headers = self.meta[meta_id]["headers"]
        horizontal_requirement = len(headers)

        # STEP 1:
        # - add "False" flag to rows
        # - if something
        _container = []
        for container_id, row in enumerate(container):
            _row = row
            if len(row) != horizontal_requirement:
                missing = horizontal_requirement - len(row)
                for x in range(missing):
                    _row.append(False)
                container[container_id] = _row

        # STEP 2:
        # - iterate each row, frontadding old data and
        # - adding the last value
        columns = self.split_array_vertically(container)
        # print(columns) # index, :1, :false

        for x, column in enumerate(columns):
            if x == 0: continue # ignore index
            _column = []

            found_data, last_data, fill_later = False, False, False

            for data in column:
                if data == False:
                    if found_data:
                        _column.append(last_data)
                    else:
                        print("cleaning found, fill later flagged")
                        _column.append("FILL_LATER")
                        fill_later = True
                else:
                    found_data, last_data = True, data
                    _column.append(data)
                    if fill_later:
                        _column = [c.replace("FILL_LATER", data) for c in _column]
                        fill_later = False

            columns[x] = _column

        rows = self.vertical_combine(columns)

        # great

        self.meta.append({
            "container": rows,
            "headers": headers
        })

        return len(self.meta)-1

    """
    generate a bridge as a line chart
    """
    def meta_line_chart(self, saveloc, options):
        from fdates import parse
        import json

        json_object = {
            "type": "line-chart",
            "pure": [],
            "headers": [],
            "options": {
                # "vAxis": { "logScale": True, "minValue": 0 },
                "chart": {
                    "title": False
                },
                "series": {

                },
                "axes": {
                    "y": {

                    }
                }
            }
        }

        # meta get

        mid = options["use"]
        md = self.meta[mid]
        mdheaders, container = md["headers"], md["container"]

        # SOLVING THE PURE OBJECT

        definitions = options["names"]

        # inserting the pure line-by-line objects
        pure_cache = []
        _pure_row = []
        for row in container:
            # print(row)
            _row = []
            for i, typestr in enumerate(definitions):
                if typestr == False: continue
                # print(typestr)
                type, name = typestr.split(":")
                # type defs for google chart
                if type == "date":
                    pieces = parse("year/month/day", row[i])
                    _row.append([pieces["year"], pieces["month"]-1, pieces["day"]])
                elif type == "number":
                    # if row[i] == ".":
                        # _row.append( float("{:.2f}".format(float(last_value))) )
                    # else:
                    # print(row[i])
                    _row.append( float("{:.2f}".format(float(row[i]))) )
                elif type == "string":
                    _row.append( str(row[i]) )
                elif type == "ignore":
                    continue
                # last_value = row[i]
            pure_cache.append(_row)

        json_object["pure"] = pure_cache

        # HEADERS
        headers = []
        for i, typestr in enumerate(definitions):
            if typestr == False: continue
            type, name = typestr.split(":")
            if type != "ignore":
                headers.append([type, name])
        json_object["headers"] = headers

        # OPTIONS
        json_object["options"]["width"] = "100%"
        json_object["options"]["height"] = 300
        json_object["options"]["chart"]["title"] = ""

        # managing left series
        if "left" in options:
            for rowid in options["left"]:
                json_object["options"]["series"][str(rowid-1)] = {"axis":"Left"}
            json_object["options"]["axes"]["y"]["Left"] = {"label": ""}

        # managing right series
        if "right" in options:
            for rowid in options["right"]:
                json_object["options"]["series"][str(rowid-1)] = {"axis":"Right"}
                json_object["options"]["axes"]["y"]["Right"] = {"label": ""}

        # managing random series
        if "random" in options:
            import random
            for rowid in options["random"]:
                randomseries = str(random.randint(1, 100))
                json_object["options"]["series"][str(rowid-1)] = {"axis": randomseries}
                json_object["options"]["axes"]["y"][randomseries] = {"label": ""}

        open(saveloc, "w+").write(json.dumps(json_object, indent=3))
