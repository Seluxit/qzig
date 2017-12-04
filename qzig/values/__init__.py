import bellows.zigbee.zcl.clusters.general as general_clusters
import bellows.zigbee.zcl.clusters.measurement as measurement_clusters
import bellows.zigbee.zcl.clusters.homeautomation as homeautomation_clusters

from qzig.values import onoff, identify, temperature, humidity, diagnostics, ota, power, poll, alarm, kaercher


def get_value_class(cluster_id, manufacturer):
    if cluster_id == general_clusters.OnOff.cluster_id:
        values = [onoff.OnOff,
                  onoff.OnTime,
                  onoff.OnTimeout]
        if manufacturer == "Kaercher":
            values.append(onoff.BlockageCounter)
        return values
    elif cluster_id == general_clusters.Identify.cluster_id:
        return identify.Identify
    elif cluster_id == measurement_clusters.TemperatureMeasurement.cluster_id:
        return temperature.Temperature
    elif cluster_id == measurement_clusters.RelativeHumidity.cluster_id:
        return humidity.Humidity
    elif cluster_id == homeautomation_clusters.Diagnostic.cluster_id:
        return [diagnostics.DiagnosticsRetries,
                diagnostics.DiagnosticsRssi,
                diagnostics.DiagnosticsLinkQuality]
    elif cluster_id == general_clusters.Ota.cluster_id:
        return ota.Ota
    elif cluster_id == general_clusters.Alarms.cluster_id:
        return alarm.AlarmResetAll
    elif cluster_id == general_clusters.PowerConfiguration.cluster_id:
        return power.PowerConfiguration
    elif cluster_id == general_clusters.PollControl.cluster_id:
        return [poll.PollControlCheckInInterval,
                poll.PollControlLongPollInterval,
                poll.PollControlShortPollInterval,
                poll.PollControlFastPollTimeout,
                poll.PollControlFastPollStop]
    elif cluster_id == kaercher.KaercherFallback.cluster_id:
        return [kaercher.FallbackEnable,
                kaercher.FallbackOnline,
                kaercher.FallbackStartTime,
                kaercher.FallbackDuration,
                kaercher.FallbackInterval]
    elif cluster_id == kaercher.KaercherDeviceState.cluster_id:
        return [kaercher.DeviceState,
                kaercher.DeviceStateOtaUpdate,
                kaercher.DeviceStateValueError]
