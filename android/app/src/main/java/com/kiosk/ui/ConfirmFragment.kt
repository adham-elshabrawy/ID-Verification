package com.kiosk.ui

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import com.kiosk.R
import com.kiosk.databinding.FragmentConfirmBinding

class ConfirmFragment : Fragment() {
    
    private var _binding: FragmentConfirmBinding? = null
    private val binding get() = _binding!!
    private val args: ConfirmFragmentArgs by navArgs()
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentConfirmBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        binding.textName.text = "Hi ${args.employeeName}, confirm Clock ${args.eventType}"
        
        binding.buttonConfirm.setOnClickListener {
            // Create time event
            val action = ConfirmFragmentDirections.actionConfirmFragmentToSuccessFragment(
                eventType = args.eventType
            )
            findNavController().navigate(action)
        }
        
        binding.buttonCancel.setOnClickListener {
            findNavController().popBackStack()
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}

