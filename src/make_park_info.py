import pickle

if __name__=='__main__':

    park_info = {}
    park_info['east_mount_falcon']  = {'pretty_name':'East Mount Falcon', 'lat':39.646865, 'lon':-105.196314, 'capacity': 49}
    park_info['east_three_sisters'] = {'pretty_name':'East Three Sisters', 'lat':39.623484, 'lon':-105.345841, 'capacity':26}
    park_info['east_white_ranch']   = {'pretty_name':'East White Ranch', 'lat':39.798109, 'lon':-105.246799, 'capacity':51}
    park_info['lair_o_the_bear']    = {'pretty_name':"Lair O' The Bear", 'lat':39.665616, 'lon':-105.258430, 'capacity':97}
    park_info['mount_galbraith']    = {'pretty_name':'Mount Galbraith', 'lat':39.774085, 'lon':-105.253516, 'capacity':27}
    park_info['west_mount_falcon']  = {'pretty_name':'West Mount Falcon', 'lat':39.637136, 'lon':-105.239178, 'capacity':62}
    park_info['west_three_sisters'] = {'pretty_name':'West Three Sisters', 'lat':39.624941, 'lon':-105.360398, 'capacity':49}

    with open('./data/park_info.pkl', 'wb') as f:
            pickle.dump(park_info, f)