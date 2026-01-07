package com.kiosk.ui

import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import com.kiosk.R
import com.kiosk.databinding.FragmentSuccessBinding

class SuccessFragment : Fragment() {
    
    private var _binding: FragmentSuccessBinding? = null
    private val binding get() = _binding!!
    private val args: SuccessFragmentArgs by navArgs()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentSuccessBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        binding.textMessage.text = "Clock ${args.eventType} successful!"
        
        // Auto-return to home after 3 seconds
        Handler(Looper.getMainLooper()).postDelayed({
            if (findNavController().currentDestination?.id == R.id.successFragment) {
                findNavController().popBackStack(R.id.homeFragment, false)
            }
        }, 3000)
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

