import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { Grid, Link, Button, Paper, TextField, Typography } from "@mui/material";

function Login({ setIsLoggedIn, setUser }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    const handleLogin = (e) => {
        e.preventDefault();
        axios.post("http://localhost:3001/login", { email, password }, { withCredentials: true })
            .then(result => {
                if (result.data === "Success") {
                    axios.get('http://localhost:3001/user', { withCredentials: true })
                        .then(response => {
                            if (response.data.user) {
                                setIsLoggedIn(true);
                                setUser({
                                    email: response.data.user.email,
                                    name: response.data.user.name
                                });
                                navigate("/home", { state: { user: response.data.user } });
                            }
                        });
                } else {
                    alert("Login failed");
                }
            })
            .catch(err => console.log(err));
    };

    return (
        <Grid align="center">
            <Paper style={{ padding: "2rem", margin: "100px auto", borderRadius: "1rem" }}>
                <Typography component="h1" variant="h5">Login</Typography>
                <form onSubmit={handleLogin}>
                    <TextField label="Email" fullWidth variant="outlined" type="email" placeholder="Enter Email" onChange={(e) => setEmail(e.target.value)} />
                    <TextField label="Password" fullWidth variant="outlined" type="password" placeholder="Enter Password" onChange={(e) => setPassword(e.target.value)} />
                    <Button variant="contained" type="submit">Login</Button>
                </form>
                <p>Don't have an account? <Link href="/signup">SignUp</Link></p>
            </Paper>
        </Grid>
    );
}

export default Login;
