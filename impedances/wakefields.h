#ifndef WAKEFIELDS_H
#define WAKEFIELDS_H


#include <fstream>
#include "bunch.h"


/**
 * @class Wakefields
 * @author Kevin Li
 * @date March 2013
 * @brief Class for creation and management of wakefields from impedance sources
 *
 * @copyright CERN
 */

class Wakefields
{
public:
    Wakefields(double Rs_r, double fr, double Q_r,
               double Rs_z, double fz, double Q_z);
    ~Wakefields() { };

    double wake_rewall(double z);
    double wake_resonator_r(double z);
    double wake_resonator_z(double z);

    void track(Bunch& bunch);

    double kick_x, kick_y, kick_z;
    double alpha_r, alpha_z;
    double omega_r, omegabar_r, omega_z, omegabar_z;
    double Q_r, Q_z;
    double Rs_r, Rs_z;
};


#endif
