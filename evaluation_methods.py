import os
import glob
import pandas as pd


def select_best_weight(model_name):
    csv_path = "/media/data1/save_model_weight"
    model_csv_list = glob.glob(os.path.join(csv_path, model_name + "*.csv"))

    drone_list = []
    satellite_list = []

    csv_150_list = list(filter(lambda i: "150" in i, model_csv_list))
    csv_200_list = list(filter(lambda i: "200" in i, model_csv_list))
    csv_250_list = list(filter(lambda i: "250" in i, model_csv_list))
    csv_300_list = list(filter(lambda i: "300" in i, model_csv_list))
    csv_lists = [csv_150_list, csv_200_list, csv_250_list, csv_300_list]

    for csv_list in csv_lists:
        drone_recall1_max = 0
        drone_csv_index = None
        satellite_recall1_max = 0
        satellite_csv_index = None
        for csv in csv_list:
            table = pd.read_csv(csv, index_col=0)
            drone_recall1 = table.at["recall@1", "drone_max"]
            satellite_recall1 = table.at["recall@1", "satellite_max"]
            if satellite_recall1 > satellite_recall1_max:
                satellite_recall1_max = satellite_recall1
                satellite_csv_index = csv

            if drone_recall1 > drone_recall1_max:
                drone_recall1_max = drone_recall1
                drone_csv_index = csv

        drone_list.append(drone_csv_index)
        satellite_list.append(satellite_csv_index)

    return drone_list, satellite_list


def evaluate_adaption_rate(model_name):
    drone_list, satellite_list = select_best_weight(model_name)
    evaluate_drone_height = 0
    evaluate_satellite_height = 0

    for csv in drone_list:
        table = pd.read_csv(csv, index_col=0)
        max_drone_height_recall1 = table.at["recall@1", "drone_max"]
        evaluate_drone_height += max_drone_height_recall1
    for csv in satellite_list:
        table = pd.read_csv(csv, index_col=0)
        max_satellite_height_recall1 = table.at["recall@1", "satellite_max"]
        evaluate_satellite_height += max_satellite_height_recall1

    return evaluate_satellite_height/evaluate_drone_height


def evaluate_stability(model_name):

    drone_list, satellite_list = select_best_weight(model_name)
    # print(drone_list)
    # print(satellite_list)
    evaluate_value_drone_height = {}
    evaluate_value_satellite_height = {}
    for csv in drone_list:
        for height in ["150", "200", "250", "300"]:
            if height in csv:
                table = pd.read_csv(csv, index_col=0)
                evaluate_value_drone_height[height] = table.at["recall@1", "drone_max"]
    for csv in satellite_list:
        for height in ["150", "200", "250", "300"]:
            if height in csv:
                table = pd.read_csv(csv, index_col=0)
                evaluate_value_satellite_height[height] = table.at["recall@1", "satellite_max"]
    delta_drone_AP1 = (evaluate_value_drone_height["200"] - evaluate_value_drone_height["150"])/50
    delta_drone_AP2 = (evaluate_value_drone_height["250"] - evaluate_value_drone_height["200"])/50
    delta_drone_AP3 = (evaluate_value_drone_height["300"] - evaluate_value_drone_height["250"])/50
    delta_drone_list = [delta_drone_AP1, delta_drone_AP2, delta_drone_AP3]
    average_drone = sum(delta_drone_list)/len(delta_drone_list)
    stability_drone = {"delta_drone": delta_drone_list, "average_drone": average_drone}

    delta_satellite_AP1 = (evaluate_value_satellite_height["200"] - evaluate_value_satellite_height["150"])/50
    delta_satellite_AP2 = (evaluate_value_satellite_height["250"] - evaluate_value_satellite_height["300"])/50
    delta_satellite_AP3 = (evaluate_value_satellite_height["300"] - evaluate_value_satellite_height["250"])/50
    delta_satellite_list = [delta_satellite_AP1, delta_satellite_AP2, delta_satellite_AP3]
    average_satellite = sum(delta_satellite_list)/len(delta_drone_list)
    stability_satellite = {"delta_drone": delta_satellite_list, "average_drone": average_satellite}

    return stability_drone, stability_satellite

if __name__ == '__main__':
    print(evaluate_stability("resnet"))
    adaption = evaluate_adaption_rate("resnet")
    print(adaption)
