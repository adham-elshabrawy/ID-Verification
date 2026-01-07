package com.kiosk.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import com.kiosk.R
import com.kiosk.databinding.FragmentHomeBinding

class HomeFragment : Fragment() {
    
    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        binding.buttonClockIn.setOnClickListener {
            val action = HomeFragmentDirections.actionHomeFragmentToCameraFragment(eventType = "IN")
            findNavController().navigate(action)
        }
        
        binding.buttonClockOut.setOnClickListener {
            val action = HomeFragmentDirections.actionHomeFragmentToCameraFragment(eventType = "OUT")
            findNavController().navigate(action)
        }
        
        // Long press for admin (hidden feature)
        binding.root.setOnLongClickListener {
            findNavController().navigate(R.id.adminLoginFragment)
            true
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

