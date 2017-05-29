import bellows.zigbee.zcl.clusters.general as general_clusters
import bellows.zigbee.zcl.clusters.measurement as measurement_clusters

from qzig.values import onoff, identify, temperature


def get_value_class(cluster_id):
    if cluster_id == general_clusters.OnOff.cluster_id:
        return onoff.OnOff
    elif cluster_id == general_clusters.Identify.cluster_id:
        return identify.Identify
    elif cluster_id == measurement_clusters.TemperatureMeasurement.cluster_id:
        return temperature.Temperature
