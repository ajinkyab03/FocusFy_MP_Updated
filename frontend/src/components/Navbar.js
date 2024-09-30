// import React from 'react'
// import { Link } from 'react-router-dom'
// import toast from 'react-hot-toast'
// import logo from '../assets/logo.png'
// import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'
// import {faHouse} from "@fortawesome/free-solid-svg-icons"
// import {faCircleInfo} from "@fortawesome/free-solid-svg-icons"
// import {faAddressBook} from "@fortawesome/free-solid-svg-icons"


// const Navbar = () => {
//   return (
//     <div className=' fixed top-0 left-0 flex ml-[80px] justify-evenly h-[100px] w-[80%] bg-blue-400 bg-opacity-50 mt-[20px] pt-[20px] rounded-xl'>
//         <div className=''>
//             {/* <img src={logo} alt="" className='w-[200px] h-[100px] mt-[-25px]' /> */}
//         </div>

//         <div className='h-full w-full'>
//             <ul className='flex justify-evenly items-center p-[10px]'>
//                 <Link to='/'><li><FontAwesomeIcon icon={faHouse} className='h-[30px]' /></li></Link>
//                 <Link to='/about'><li><FontAwesomeIcon icon={faCircleInfo} className='h-[30px]'/></li></Link>
//                 <Link to='/contact'><li><FontAwesomeIcon icon={faAddressBook} className='h-[30px]' /></li></Link>
//             </ul>
//         </div>

//     </div>
//   )
// }

// export default Navbar

import React from 'react';
import { Link } from 'react-router-dom';
import AppBar from '@mui/material/AppBar';
import Toolbar from '@mui/material/Toolbar';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import Logout from './Logout';

export const Navbar = ({ isLoggedIn, setIsLoggedIn }) => {
    const button={marginRight:'20px', fontSize:'1.2rem', fontWeight:'700', padding:'0.3rem 1.4rem'}
    return (
            <AppBar sx={{ bgcolor: '#333' }}>
                <Toolbar>
                    <Typography variant="h4" component="div" sx={{ flexGrow: 1 }}>
                        Tech Coffee Break
                    </Typography>
                    {!isLoggedIn ? (
                        <>
                            <Button variant="contained" style={button} color="error" component={Link} to="/login">
                                Login 
                            </Button>

                            <Button variant="contained" style={button} color="success" component={Link} to="/signup">
                                Signup
                            </Button>
                        </>
                    ) : (
                        <Logout setIsLoggedIn={setIsLoggedIn} />
                    )}
                </Toolbar>
            </AppBar>
    );
};