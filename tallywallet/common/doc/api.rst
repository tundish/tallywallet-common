..  Titling
    ##++::==~~--''``

Programming API
:::::::::::::::

.. automodule:: tallywallet.common.exchange
   :members: Exchange

Examples
::::::::

=====   =============== ======= ======= ======= ======= ===============
date                    asset   asset   capital expense trading
=====   =============== ======= ======= ======= ======= ===============
Jan 1   Opening balance CAD 200 USD 0   CAD 200 CAD 0   USD 0 CAD 0
Jan 2   1 USD==1.20CAD  CAD-120 USD 100    .       .    USD 100 CAD 120
 "      Balance         CAD 80  USD 100 CAD 200 CAD 0   USD 100 CAD 120
Jan 3   1 USD==1.30CAD     .    USD-40     .    CAD 52  USD-40 CAD 52
 "      Balance         CAD 80  USD 60  CAD 200 CAD 52  USD 60 CAD-68
Jan 5   1 USD==1.25CAD  CAD 75  USD-60     .       .    USD-60 CAD 75
 "      Balance         CAD 155 USD 0   CAD 200 CAD 52  USD 0  CAD 07
Jan 7   Buy food        CAD-20     .       .    CAD 20     .      
 "      Balance         CAD 135 USD 0   CAD 200 CAD 72  USD 0  CAD 07
=====   =============== ======= ======= ======= ======= ===============
