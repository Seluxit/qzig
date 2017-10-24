import bellows.zigbee.zcl.clusters.general as general_clusters
import bellows.zigbee.zcl.clusters.measurement as measurement_clusters
import bellows.zigbee.zcl.clusters.homeautomation as homeautomation_clusters

from qzig.values import onoff, identify, temperature, humidity, diagnostics, ota, kaercher


def get_value_class(cluster_id):
    if cluster_id == general_clusters.OnOff.cluster_id:
        return [onoff.OnOff, onoff.OnTimeout]
    elif cluster_id == general_clusters.Identify.cluster_id:
        return identify.Identify
    elif cluster_id == measurement_clusters.TemperatureMeasurement.cluster_id:
        return temperature.Temperature
    elif cluster_id == measurement_clusters.RelativeHumidity.cluster_id:
        return humidity.Humidity
    elif cluster_id == homeautomation_clusters.Diagnostic.cluster_id:
        return diagnostics.Diagnostics
    elif cluster_id == general_clusters.Ota.cluster_id:
        return ota.Ota
    elif cluster_id == 0xC001:
        return kaercher.DeviceState
