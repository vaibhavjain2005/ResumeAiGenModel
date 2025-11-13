import React from 'react'
import { Link } from 'react-router-dom';
function Logo({ size }) {
    return (
        <div><Link aria-current="page" to={'/'} className='text-white'>
            <div className='flex justify-center'>
                <div className='flex flex-col justify-center'>
                    <p style={{ fontFamily: '"Momo Signature", cursive' }} className={`text-${size}`}>Resume</p>
                </div>
                <div className='flex flex-col justify-center'>
                    <p className='font-Inter text-xl'>Chef.</p>
                </div>
                </div>

        </Link></div>
    )
}

export default Logo