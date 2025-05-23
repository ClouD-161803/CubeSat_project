#include <iostream>
#include <vector>
#include <string>

class component{
    public:
        std::string name;
        float power;
};

class sensor: public component{
    private:
        int data_rate;
    public:
        sensor(std::string sensor_name, float sensor_power, int freq){
            name = sensor_name;
            power = sensor_power;
            data_rate = freq;
        }
        int getDataRate(){
            return data_rate;
        }
        
};

class computer: public component{
    private:
        int max_data_rate;

    public:
        computer(std::string obc_name, float obc_power, int obc_data_rate){
            name = obc_name;
            power = obc_power;
            max_data_rate = obc_data_rate;
        }
        int getMaxDataRate(){
            return max_data_rate;
        }

};

class commsUnit: public component{
    private:
        int bandwidth;

    public:
        commsUnit(std::string comms_name, float comms_power, int comms_bandwidth){
            name = comms_name;
            power = comms_power;
            bandwidth = comms_bandwidth;
        }
        int getBandwidth(){
            return bandwidth;
        }
};

class cubesat{
    private:
        std::vector<sensor*> sensors;
        std::vector<computer*> comp;
        std::vector<commsUnit*> comms;
    
    public:
        cubesat(){
            sensors = {};
            comp = {};
            comms = {};
        }

        void addSensor(std::string sensor_name, float sensor_power, int freq){
            sensor* s = new sensor(sensor_name, sensor_power, freq);
            sensors.push_back(s);
        }


        void addComputer(std::string obc_name, float obc_power, int obc_data_rate){
            computer* c = new computer(obc_name, obc_power, obc_data_rate);
            comp.push_back(c);
        }

        void addComms(std::string comms_name, float comms_power, int comms_bandwidth){
            commsUnit* c = new commsUnit(comms_name, comms_power, comms_bandwidth);
            comms.push_back(c);
        }
        void analyse(){
            float total_power = 0;
            int total_sensor_data_rate = 0;
            int total_comp_data_rate = 0;
            int total_comms_bandwidth = 0;
            
            std::cout << "Sensor list: ";
            for (int i = 0; i < sensors.size(); i++){
                total_power += sensors[i]->power;
                total_sensor_data_rate += sensors[i]->getDataRate();
                std::cout << sensors[i]->name << ", ";
            }
            std::cout << std::endl;
            std::cout << "Computer list: ";
            for (int i = 0; i < comp.size(); i++){
                total_power += comp[i]->power;
                total_comp_data_rate += comp[i]->getMaxDataRate();
                std::cout << comp[i]->name << ", ";
            }
            std::cout << std::endl;
            std::cout << "Comms list: ";
            for (int i = 0; i < comms.size(); i++){
                total_power += comms[i]->power;
                total_comms_bandwidth += comms[i]->getBandwidth();
                std::cout << comms[i]->name << ", ";
            }
            std::cout << std::endl;

            std::cout << "Total Power: " << total_power << std::endl;
            std::cout << "Total Sensor Data Rate: " << total_sensor_data_rate << std::endl;
            std::cout << "Total Computer Data Rate: " << total_comp_data_rate << std::endl;
            std::cout << "Total Comms Bandwidth: " << total_comms_bandwidth << std::endl;
            
            //Check cubesat is functional
            if (total_sensor_data_rate > total_comp_data_rate){
                std::cout << "Sensor data rate exceeds computer data rate!" << std::endl;
            }
            if (total_comp_data_rate < total_comms_bandwidth){
                std::cout << "Comms bandwidth is less than computer data rate!" << std::endl;
            }

        }


};

int main(){
    cubesat c;
    c.addSensor("Thermocouple", 0.1, 100);
    c.addComputer("OBC", 2.5, 200);
    c.addComms("Comms", 1.5, 300);
    c.analyse();
    return 0;
}