import os
import time
import random
import numpy as np
import warnings
import pytest


from wmm import wmm_calc as vectorized_wmm_calc



def get_test_val(path= "WMM2025_TEST_VALUE_TABLE_FOR_REPORT.txt"):
    lat = []
    lon = []
    alt = []
    time = []
    test_X = []
    test_dec = []
    test_H = []
    test_ydot = []
    test_ddec = []
    with open(path, 'r') as infile:
        for line in infile:
            values = line.split()
            if(values[0] == '#'):
                continue
            values = values
            lat.append( np.float64(values[2]))
            lon.append( np.float64(values[3]))
            alt.append( np.float64(values[1]))
            time.append( np.float64(values[0]))
            test_X.append( np.float64(values[4]))
            test_H.append( np.float64(values[7]))
            test_dec.append(np.float64(values[10]))
            test_ydot.append( np.float64(values[13]))
            test_ddec.append(np.float64(values[-1]))

    return np.array(lat), np.array(lon), np.array(alt), np.array(time), np.array(test_X), np.array(test_dec), np.array(test_H), np.array(test_ydot), np.array(test_ddec)
def get_ymd(time,lat):
    year = []
    month = []
    day = []
    for i in range(0,len(lat)):
        if(time[i] == 2025.0):
            year.append(2025)
            month.append(1)
            day.append(1)
        else:
            year.append(2027)
            month.append(7)
            day.append(2)
    year = np.array(year)
    month = np.array(month)
    day = np.array(day)
    return year, month, day
    
def vector_test_cases(which_case):
    #This test case attests that my additions of vector
    #Methods are consistent with the output from WMM previous to my changes
    #The cases are that alt, lat, lon (rtp) have
    top_dir = os.path.dirname(os.path.dirname(__file__))
    testVal_file = os.path.join(top_dir, "tests", "WMM2025_TEST_VALUE_TABLE_FOR_REPORT.txt")
    lat, lon, alt, time, test_X, test_dec, test_H, test_ydot, test_ddec = get_test_val(testVal_file)

    if(which_case == 0):#1a) All scalar
        model =  vectorized_wmm_calc()
        for i in range(0,len(lat)):
            model.setup_env(lat[i], lon[i], alt[i])
            model.setup_time(dyear=time[i])
            # old_model = wmm_calc()
            # old_model.setup_env(lat[i], lon[i], alt[i])
            vec_ans = model.get_all()
            
            # old_ans = old_model.get_all()          
            print(vec_ans, test_X[i], test_ddec[i])
            assert np.isclose(test_X[i], vec_ans['x'], rtol=0, atol=0.1)
            assert np.isclose(test_dec[i] ,vec_ans['dec'], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'], rtol=0, atol=0.1)
            assert np.isclose(test_ydot[i] , vec_ans['dy'], rtol=0, atol=0.1)
            assert np.isclose(test_ddec[i], vec_ans['ddec'], rtol=0, atol=0.01)
    elif(which_case == 1):#1b) All vector
        model2 =  vectorized_wmm_calc()
        
        model2.setup_env(lat, lon, alt)
        model2.setup_time(dyear=time)
        vec_ans = model2.get_all()
        
        for i in range(0,len(lat)):
            
            assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=0.1)

            assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
            assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
    elif(which_case == 2):#1c) 1 vector 2 scalar pos
        # print("should produce 4 warnings due to broadcasted locations being in blackout zones")
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r".*is in the blackout zone around the magnetic pole.*",
                category=UserWarning,
            )
            warnings.filterwarnings(
                "ignore",
                message=r".*is approaching the blackout zone around the magnetic pole.*",
                category=UserWarning,
            )
            for i in range(0,len(lat)):
                model =  vectorized_wmm_calc()
            
                model.setup_env(lat, lon[i], alt[i])
                model.setup_time(dyear=time)
                vec_ans = model.get_all()
                assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=0.1)
                assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
                assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
                assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
                assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
            for i in range(0,len(lat)):
                model =  vectorized_wmm_calc()
            
                model.setup_env(lat[i], lon, alt[i])
                model.setup_time(dyear=time)
                vec_ans = model.get_all()
                assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=0.1)
                assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
                assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
                assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
                assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
            for i in range(0,len(lat)):
                model =  vectorized_wmm_calc()
            
                model.setup_env(lat[i], lon[i], alt)
                model.setup_time(dyear=time)
                vec_ans = model.get_all()
                assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=0.1)
                assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
                assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
                assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
                assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
    elif(which_case == 3):#1d) 2 vector 1 scalar pos
        # 1di) vectors have the same length
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r".*is in the blackout zone around the magnetic pole.*",
                category=UserWarning,
            )
            warnings.filterwarnings(
                "ignore",
                message=r".*is approaching the blackout zone around the magnetic pole.*",
                category=UserWarning,
            )
            for i in range(0,len(lat)):
                model =  vectorized_wmm_calc()
            
                model.setup_env(lat, lon, alt[i])
                model.setup_time(dyear=time)
                vec_ans = model.get_all()
                assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=0.1)
                assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
                assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
                assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
                assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
            for i in range(0,len(lat)):
                model =  vectorized_wmm_calc()
            
                model.setup_env(lat[i], lon, alt)
                model.setup_time(dyear=time)
                vec_ans = model.get_all()
                assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=0.1)
                assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
                assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
                assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
                assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
            for i in range(0,len(lat)):
                model =  vectorized_wmm_calc()
            
                model.setup_env(lat, lon[i], alt)
                model.setup_time(dyear=time)
                vec_ans = model.get_all()
                assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=0.1)
                assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
                assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
                assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
                assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
        # 1dii) vectors have different length
    
            with pytest.raises(ValueError, match=r"The input*"):
                model.setup_env(lat[:-1], lon, alt[i])
    elif(which_case == 4):#2a) All scalar time
        model =  vectorized_wmm_calc()
        for i in range(0,len(lat)):
            model.setup_env(lat[i], lon[i], alt[i])
            if(time[i] == 2025.0):
                model.setup_time(year=2025, month= 1, day=1)
            else:
                model.setup_time(year = 2027, month= 7, day = 2)
            vec_ans = model.get_all()
            
            # old_ans = old_model.get_all()          
            assert np.isclose(test_ddec[i], vec_ans['ddec'], rtol=0, atol=0.01)
            assert np.isclose(test_X[i], vec_ans['x'], rtol=0, atol=0.1)
            assert np.isclose(test_dec[i] ,vec_ans['dec'], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'], rtol=0, atol=0.1)
            assert np.isclose(test_ydot[i] , vec_ans['dy'], rtol=0, atol=0.1)
    elif(which_case == 5):#2b) All vector time
        model =  vectorized_wmm_calc()
        model.setup_env(lat, lon, alt)
        year,month,day  = get_ymd(time, lat)
        model.setup_time(year, month, day)
        vec_ans = model.get_all()
        for i in range(0,len(lat)):
        
            assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=0.1)
            assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
            assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
    elif(which_case == 6):#2c) 1 vector 2 scalar time
        year, month, day = get_ymd(time, lat)
        for i in range(0,len(lat)):
            model =  vectorized_wmm_calc()
        
            model.setup_env(lat, lon, alt)
            model.setup_time(year[i], month[i], day)

            vec_ans = model.get_all()
            assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=.1)
            assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
            assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
        for i in range(0,len(lat)):
            model =  vectorized_wmm_calc()
        
            model.setup_env(lat, lon, alt)
            model.setup_time(year[i], month, day[i])
            vec_ans = model.get_all()
            assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=.1)
            assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
            assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
        for i in range(0,len(lat)):
            model =  vectorized_wmm_calc()
        
            model.setup_env(lat, lon, alt)
            model.setup_time(year, month[i], day[i])
            vec_ans = model.get_all()
            assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=.1)
            assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
            assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
    elif(which_case == 7):#2d) 2 vector 1 scalar time
        # 1di) vectors have the same length
        year, month, day = get_ymd(time, lat)
        for i in range(0,len(lat)):
            model =  vectorized_wmm_calc()
        
            model.setup_env(lat, lon, alt)
            model.setup_time(year, month, day[i])
            vec_ans = model.get_all()
            assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=.1)
            assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
            assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
        for i in range(0,len(lat)):
            model =  vectorized_wmm_calc()
        
            model.setup_env(lat, lon, alt)
            model.setup_time(year, month[i], day)
            vec_ans = model.get_all()
            assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=.1)
            assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
            assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
        for i in range(0,len(lat)):
            model =  vectorized_wmm_calc()
        
            model.setup_env(lat, lon, alt)
            model.setup_time(year[i], month, day)
            vec_ans = model.get_all()

            assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=.1)
            assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
            assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
        # 1dii) vectors have different length
    
        with pytest.raises(ValueError, match=r"The"):
            model.setup_time(year[i], month[i:-1], day)
            # model.setup_env(lat[:-1], lon, alt)
    elif(which_case == 8):#3a) vector dyear scalar pos
        model =  vectorized_wmm_calc()
        for i in range(0,len(lat)):
            model.setup_env(lat[i], lon[i], alt[i])
            model.setup_time(dyear=time)

            vec_ans = model.get_all()
          
            assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=0.1)
            assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
            assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
        for i in range(0,len(lat)):
            model.setup_time(dyear=time)
            model.setup_env(lat[i], lon[i], alt[i])
            

            vec_ans = model.get_all()
          
            assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=0.1)
            assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
            assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
    elif(which_case == 9):#3b) scalar dyear vector pos
        model =  vectorized_wmm_calc()
        for i in range(0,len(lat)):
            model.setup_env(lat, lon, alt)
            model.setup_time(dyear=time[i])

            vec_ans = model.get_all()
          
            assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=0.1)
            assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
            assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
        for i in range(0,len(lat)):
            model.setup_time(dyear=time[i])
            model.setup_env(lat, lon, alt)


            vec_ans = model.get_all()
          
            assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=0.1)
            assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
            assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)
    elif(which_case == 10):#3c) vector dyear vector position
        model =  vectorized_wmm_calc()
        for i in range(0,len(lat)):
            model.setup_env(lat, lon, alt)
            model.setup_time(dyear=time)

            vec_ans = model.get_all()
          
            assert np.isclose(test_ddec[i], vec_ans['ddec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_X[i], vec_ans['x'][i], rtol=0, atol=0.1)
            assert np.isclose(test_dec[i] ,vec_ans['dec'][i], rtol=0, atol=0.01)
            assert np.isclose(test_H[i] , vec_ans['h'][i], rtol=0, atol=0.1)
            assert np.isclose(test_ydot[i] , vec_ans['dy'][i], rtol=0, atol=0.1)            
        with pytest.raises(ValueError, match=r"The input*"):
   
                model =  vectorized_wmm_calc()
                model.setup_env(lat[:-1], lon, alt)
                model.setup_time(dyear=time)
                vec_ans = model.get_all()
        with pytest.raises(ValueError, match=r"The input*"):

                model =  vectorized_wmm_calc()
                model.setup_env(lat, lon[:-1], alt)
                model.setup_time(dyear=time)
                vec_ans = model.get_all()
        with pytest.raises(ValueError, match=r"The input*"):
        
                model =  vectorized_wmm_calc()
                model.setup_env(lat, lon, alt[:-1])
                model.setup_time(dyear=time)
                vec_ans = model.get_all()
        with pytest.raises(ValueError, match=r"The input*"):
               
                model =  vectorized_wmm_calc()
                model.setup_env(lat, lon, alt)
                model.setup_time(dyear=time[:-1])
                vec_ans = model.get_all()
                
        with pytest.raises(ValueError, match=r"The input*"):
                
                model =  vectorized_wmm_calc()
                model.setup_time(dyear=time[:-1])
                model.setup_env(lat, lon, alt)
                
                vec_ans = model.get_all()
        with pytest.raises(ValueError, match=r"The input*"):
                model =  vectorized_wmm_calc()
                model.setup_time(dyear=time)
                model.setup_env(lat[:-1], lon, alt)
                vec_ans = model.get_all()
    else:
         print(f'you havent created testcase {which_case} yet')
    print(f'passed test case {which_case}')
    return

def main():
    
    for i in range(0,11):
        vector_test_cases(i)
    # print('change things back please!!! here to 10 or whatever the last test case is')


    

if __name__ == "__main__":
    # model =  vectorized_wmm_calc()
    # alt = [1]
    
    # lat = np.array([1]) 
    # lon = [1]
    # print(type(alt))
    # year= [2025]
    # month = [2]
    # day = [3]
    # model.setup_env(alt,lat ,lon )
    # model.setup_time(year=year, month=month, day= day)
    # # old_model = wmm_calc()
    # # old_model.setup_env(lat[i], lon[i], alt[i])
    # vec_ans = model.get_all()
    # print('its getting caught up here?')
    main()